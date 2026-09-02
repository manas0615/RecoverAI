import requests, json, uuid, hmac, hashlib, os
from datetime import datetime, UTC
from dotenv import load_dotenv
load_dotenv('.env')

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_secret")
payload = {"event": "payment.failed", "contains": ["payment"], "payload": {"payment": {"entity": {"id": f"pay_{uuid.uuid4().hex[:12]}", "amount": 600000000, "currency": "INR", "customer_id": "cust_demo", "status": "failed", "error_code": "BAD_REQUEST_ERROR"}}}, "created_at": int(datetime.now(UTC).timestamp())}
body = json.dumps(payload, separators=(",", ":"))
sig = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
req = requests.post("http://127.0.0.1:8000/webhooks/razorpay/merch_demo", data=body, headers={"X-Razorpay-Signature": sig, "X-Razorpay-Event-Id": f"ev_{uuid.uuid4().hex[:12]}", "Content-Type": "application/json"})
