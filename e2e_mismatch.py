import requests, json, uuid, hmac, hashlib, os
from datetime import datetime, UTC
from dotenv import load_dotenv
load_dotenv('.env')

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_KEY = os.getenv("FRONTEND_API_KEY")
WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_secret")

def send_webhook(event_type, payload):
    body = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    resp = requests.post(f"{BASE_URL}/webhooks/razorpay/merch_demo", data=body, headers={"X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": event_id, "Content-Type": "application/json"})
    return resp

print("\n--- VERIFICATION MISMATCH TEST ---")
# Get the case and plink_id
resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case = next(c for c in resp.json()["cases"] if c["amount_minor"] == 550000000 and c["status"] == "OPEN")
plink_id = case["external_reference"]

# Send mismatched amount (500 INR instead of 5,500,000 INR)
paid_payload = {
    "event": "payment_link.paid",
    "contains": ["payment_link"],
    "payload": {
        "payment_link": {
            "entity": {
                "id": plink_id,
                "amount": 50000,
                "currency": "INR",
                "customer_id": "cust_demo",
                "status": "paid",
            }
        }
    },
    "created_at": int(datetime.now(UTC).timestamp()),
}
send_webhook("payment_link.paid", paid_payload)

resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case_summary = next(c for c in resp.json()["cases"] if c["case_id"] == case["case_id"])
print("Final Action Status (Mismatch):", case_summary["action_status"])
print("Final Case Status (Mismatch):", case_summary["status"])
