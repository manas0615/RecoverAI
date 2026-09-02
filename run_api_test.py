import requests
import uuid
import time
from datetime import datetime, UTC

API_KEY = "test_frontend_key_default"
BASE_URL = "http://localhost:8000"

# 1. Trigger webhook
event_payload = {
    "event": "payment.failed",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": f"pay_{uuid.uuid4().hex[:12]}",
                "amount": 50000,
                "currency": "INR",
                "customer_id": "cust_demo",
                "status": "failed",
                "error_code": "BAD_REQUEST_ERROR"
            }
        }
    }
}
import hmac
import hashlib
import json
body = json.dumps(event_payload, separators=(',', ':'))
sig = hmac.new(b"test_secret", body.encode(), hashlib.sha256).hexdigest()

resp = requests.post(f"{BASE_URL}/webhooks/razorpay", data=body, headers={"X-Razorpay-Signature": sig, "Content-Type": "application/json"})
print("Webhook:", resp.status_code, resp.text)

time.sleep(1)

cases = requests.get(f"{BASE_URL}/recovery-cases", headers={"X-API-Key": API_KEY}).json()
if not cases:
    print("No cases found")
    exit(1)

case_id = cases[0]["case_id"]
print("Analyzing case:", case_id)

resp = requests.post(f"{BASE_URL}/recovery-cases/{case_id}/analyze", headers={"X-API-Key": API_KEY})
print("Analyze:", resp.status_code)

case_detail = requests.get(f"{BASE_URL}/recovery-cases/{case_id}", headers={"X-API-Key": API_KEY}).json()
print("Action Status:", case_detail.get("action_status"))
