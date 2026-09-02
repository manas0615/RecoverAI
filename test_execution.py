from fastapi.testclient import TestClient
from recoverai.api.main import app
from recoverai.config import settings
import uuid
import json
import hmac
import hashlib
from recoverai.api.main import container

merchant_id = "merch_demo"
customer_id = "cust_demo"
amount = 45000
currency = "INR"

event_id = f"ev_{uuid.uuid4().hex[:12]}"
payment_id = f"pay_{uuid.uuid4().hex[:12]}"
event_payload = {
    "event": "payment.failed",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": payment_id,
                "amount": amount,
                "currency": currency,
                "status": "failed",
                "customer_id": customer_id,
                "error_code": "BAD_REQUEST_ERROR",
                "error_description": "Payment failed",
            }
        }
    },
    "created_at": 1690000000,
}
body = json.dumps(event_payload).encode("utf-8")
signature = hmac.new(
    settings.razorpay_webhook_secret.encode("utf-8"),
    body,
    hashlib.sha256,
).hexdigest()

client = TestClient(app)
resp = client.post(
    f"/webhooks/razorpay/{merchant_id}",
    content=body,
    headers={
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": event_id,
        "Content-Type": "application/json",
    },
)

# Get the latest case id
with container.tm.transaction() as conn:
    cur = conn.execute("SELECT case_id FROM recovery_cases ORDER BY ROWID DESC LIMIT 1;")
    row = cur.fetchone()
    case_id = dict(row)["case_id"]

print(f"Created Case: {case_id}")

resp2 = client.post(
    f"/recovery-cases/{case_id}/analyze",
    headers={"X-API-Key": settings.frontend_api_key},
)

print(f"Analyze Status: {resp2.status_code}")
try:
    print(json.dumps(resp2.json(), indent=2))
except:
    pass

# Print the action details
with container.tm.transaction() as conn:
    cur = conn.execute("SELECT action_id, status, workflow_execution_reference, external_reference, failure_reason FROM recovery_actions WHERE case_id = ?", (case_id,))
    row = cur.fetchone()
    print(f"Action DB State: {dict(row)}")
