import json
import urllib.request
import base64

payload = {
    "amount": 10000,
    "currency": "INR",
    "reference_id": "test_script_001",
    "description": "Recovery Payment for case test",
}
url = "https://api.razorpay.com/v1/payment_links"
data = json.dumps(payload).encode("utf-8")
auth_str = "rzp_test_TURMnQDelKdhAj:OrVS1leayjv74bcG5JzA1lEr"
auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")

req = urllib.request.Request(
    url,
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_bytes}",
    },
    method="POST",
)
with urllib.request.urlopen(req) as response:
    response_data = json.loads(response.read().decode("utf-8"))
    print(json.dumps(response_data, indent=2))
