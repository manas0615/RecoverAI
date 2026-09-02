import requests
import json
import uuid
import hmac
import hashlib
from datetime import datetime, UTC
import os
from dotenv import load_dotenv

load_dotenv('.env')

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_KEY = os.getenv("FRONTEND_API_KEY")
N8N_KEY = os.getenv("N8N_API_KEY")
WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_secret")

print(f"Testing against backend at {BASE_URL}")

def send_webhook(event_type, payload):
    body = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    resp = requests.post(
        f"{BASE_URL}/webhooks/razorpay/merch_demo",
        data=body,
        headers={
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": event_id,
            "Content-Type": "application/json",
        },
    )
    return resp, event_id

# 1. Health check
print("\n--- 1. Health Check ---")
resp = requests.get(f"{BASE_URL}/health")
print(resp.json())
assert resp.status_code == 200

# 2. Ingest Case (Test 1)
print("\n--- 2. Ingest Case ---")
amount = 120000
currency = "INR"
customer_id = "cust_demo"
payload = {
    "event": "payment.failed",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": f"pay_{uuid.uuid4().hex[:12]}",
                "amount": amount,
                "currency": currency,
                "customer_id": customer_id,
                "status": "failed",
                "error_code": "BAD_REQUEST_ERROR",
            }
        }
    },
    "created_at": int(datetime.now(UTC).timestamp()),
}
resp, event_id = send_webhook("payment.failed", payload)
print("Webhook Response:", resp.text)
assert resp.status_code == 200

# Webhook Duplicate
print("\n--- Webhook Duplicate ---")
body = json.dumps(payload, separators=(",", ":"))
signature = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
resp_dup = requests.post(
    f"{BASE_URL}/webhooks/razorpay/merch_demo",
    data=body,
    headers={"X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": event_id, "Content-Type": "application/json"},
)
print("Duplicate Webhook Response:", resp_dup.text)
assert resp_dup.json()["status"] == "duplicate"

# Webhook Invalid Signature
print("\n--- Webhook Invalid Signature ---")
resp_inv = requests.post(
    f"{BASE_URL}/webhooks/razorpay/merch_demo",
    data=body,
    headers={"X-Razorpay-Signature": "invalid", "X-Razorpay-Event-Id": f"ev_{uuid.uuid4().hex[:12]}", "Content-Type": "application/json"},
)
print("Invalid Sig Response:", resp_inv.status_code, resp_inv.text)
assert resp_inv.status_code == 400

# Find Case
print("\n--- Find Case ---")
resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
cases = resp.json()["cases"]
case = next((c for c in cases if c["customer_id"] == customer_id and c["amount_minor"] == amount and c["status"] == "OPEN"), None)
print("Case Found:", case["case_id"])
case_id = case["case_id"]

# 3. Analyze Case (Test 2)
print("\n--- 3. Analyze Case ---")
resp = requests.post(f"{BASE_URL}/recovery-cases/{case_id}/analyze", headers={"X-API-Key": FRONTEND_KEY})
print("Analyze Response:", resp.text)
assert resp.status_code == 200

# 4. Policy Approve / Real Execute (Test 3 & 5)
print("\n--- 4. Execute Action (MCP) ---")
act_id = f"act_{uuid.uuid4().hex[:8]}"
resp = requests.post(
    f"{BASE_URL}/mcp/execute",
    headers={"X-API-Key": N8N_KEY},
    json={"tool": "create_payment_link", "args": {"case_id": case_id, "action_id": act_id}},
)
print("Execute Response:", resp.text)
assert resp.status_code == 200

resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case_summary = next(c for c in resp.json()["cases"] if c["case_id"] == case_id)
print("Action Status:", case_summary["action_status"])
print("External Ref:", case_summary["external_reference"])
plink_id = case_summary["external_reference"]

# 5. Verification / Webhook Test (Test 5)
print("\n--- 5. Payment Verification Webhook ---")
paid_payload = {
    "event": "payment_link.paid",
    "contains": ["payment_link"],
    "payload": {
        "payment_link": {
            "entity": {
                "id": plink_id,
                "amount": amount,
                "currency": currency,
                "customer_id": customer_id,
                "status": "paid",
            }
        }
    },
    "created_at": int(datetime.now(UTC).timestamp()),
}
resp_paid, _ = send_webhook("payment_link.paid", paid_payload)
print("Payment Webhook Response:", resp_paid.text)
assert resp_paid.status_code == 200

resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case_summary = next(c for c in resp.json()["cases"] if c["case_id"] == case_id)
print("Final Action Status:", case_summary["action_status"])
print("Final Case Status:", case_summary["status"])

print("\n--- Closed Case Protection ---")
resp = requests.post(f"{BASE_URL}/recovery-cases/{case_id}/analyze", headers={"X-API-Key": FRONTEND_KEY})
print("Analyze Closed Case Response:", resp.status_code, resp.text)
assert resp.status_code == 400

print("\n--- Analytics ---")
resp = requests.get(f"{BASE_URL}/analytics", headers={"X-API-Key": FRONTEND_KEY})
print(resp.text)

print("\n--- Audit Trail ---")
resp = requests.get(f"{BASE_URL}/recovery-cases/{case_id}/timeline", headers={"X-API-Key": FRONTEND_KEY})
print(json.dumps(resp.json(), indent=2))
