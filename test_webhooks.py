import urllib.request
import base64
import json
from recoverai.config import settings

url = "https://api.razorpay.com/v1/webhooks"
auth_str = f"{settings.razorpay_key_id}:{settings.razorpay_key_secret}"
auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")

req = urllib.request.Request(
    url,
    headers={"Authorization": f"Basic {auth_bytes}"},
    method="GET",
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode())
