import urllib.request
import json
import base64
from recoverai.config import settings

url = "https://api.razorpay.com/v1/payment_links"
payload = {
    "amount": 1000,
    "currency": "INR",
    "reference_id": "test_ref_001",
    "description": "Recovery Payment"
}
data = json.dumps(payload).encode("utf-8")
auth_str = f"{settings.razorpay_key_id}:{settings.razorpay_key_secret}"
auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")

req = urllib.request.Request(
    url, data=data,
    headers={"Content-Type": "application/json", "Authorization": f"Basic {auth_bytes}"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        print("SUCCESS")
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"FAILED: {e.code}")
    print(e.read().decode())
