import requests, json, uuid, hmac, hashlib, os
from datetime import datetime, UTC
from dotenv import load_dotenv
load_dotenv('.env')

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_KEY = os.getenv("FRONTEND_API_KEY")
N8N_KEY = os.getenv("N8N_API_KEY")
WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_secret")

def send_webhook(event_type, payload):
    body = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    resp = requests.post(f"{BASE_URL}/webhooks/razorpay/merch_demo", data=body, headers={"X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": event_id, "Content-Type": "application/json"})

print("\n--- DENIAL TEST ---")
amount = 550000000 # Different amount to avoid pure idempotent deduplication of same event payload
payload = {"event": "payment.failed", "contains": ["payment"], "payload": {"payment": {"entity": {"id": f"pay_{uuid.uuid4().hex[:12]}", "amount": amount, "currency": "INR", "customer_id": "cust_demo", "status": "failed", "error_code": "BAD_REQUEST_ERROR"}}}, "created_at": int(datetime.now(UTC).timestamp())}
send_webhook("payment.failed", payload)
resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case_id = next(c["case_id"] for c in resp.json()["cases"] if c["amount_minor"] == amount and c["status"] == "OPEN")

requests.post(f"{BASE_URL}/recovery-cases/{case_id}/analyze", headers={"X-API-Key": FRONTEND_KEY})
act_id = f"act_{uuid.uuid4().hex[:8]}"
resp = requests.post(f"{BASE_URL}/mcp/execute", headers={"X-API-Key": N8N_KEY}, json={"tool": "create_payment_link", "args": {"case_id": case_id, "action_id": act_id}})
print("Denial Execute Response:", resp.text)

resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case_summary = next(c for c in resp.json()["cases"] if c["case_id"] == case_id)
print("Denial Action Status:", case_summary["action_status"])
