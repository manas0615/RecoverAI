import requests

resp = requests.get(
    "https://api.razorpay.com/v1/webhooks",
    auth=("rzp_test_TURMnQDelKdhAj", "OrVS1leayjv74bcG5JzA1lEr")
)
print(resp.status_code, resp.text)
