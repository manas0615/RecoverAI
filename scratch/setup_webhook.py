import os
import json
import urllib.request
import base64

key_id = os.environ.get("RAZORPAY_KEY_ID")
key_secret = os.environ.get("RAZORPAY_KEY_SECRET")

auth = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()

data = {
    "url": "https://yareli-overfat-debauchedly.ngrok-free.dev/webhooks/razorpay/merch_demo",
    "alert_email": "test@example.com",
    "secret": "my_secure_webhook_secret_123",
    "events": {
        "payment.failed": True,
        "payment_link.paid": True
    }
}

req = urllib.request.Request(
    "https://api.razorpay.com/v1/webhooks",
    data=json.dumps(data).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth}"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.status)
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode())
