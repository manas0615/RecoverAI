import requests

auth = ("rzp_test_TURMnQDelKdhAj", "OrVS1leayjv74bcG5JzA1lEr")

# Create Order
order_payload = {
  "amount": 50000,
  "currency": "INR",
  "receipt": "receipt_1"
}
resp = requests.post("https://api.razorpay.com/v1/orders", json=order_payload, auth=auth)
print("Order Response:", resp.status_code, resp.text)
order_id = resp.json()["id"]

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Razorpay Test</title>
</head>
<body>
    <button id="rzp-button1">Pay</button>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
        var options = {{
            "key": "rzp_test_TURMnQDelKdhAj",
            "amount": "50000",
            "currency": "INR",
            "name": "Acme Corp",
            "description": "Test Transaction",
            "order_id": "{order_id}",
            "handler": function (response){{
                console.log(response);
            }},
            "prefill": {{
                "name": "Gaurav Kumar",
                "email": "gaurav.kumar@example.com",
                "contact": "9000090000"
            }},
            "theme": {{
                "color": "#3399cc"
            }}
        }};
        var rzp1 = new Razorpay(options);
        rzp1.on('payment.failed', function (response){{
                console.log("Failed", response);
        }});
        document.getElementById('rzp-button1').onclick = function(e){{
            rzp1.open();
            e.preventDefault();
        }}
    </script>
</body>
</html>
"""
with open("fake_merchant.html", "w") as f:
    f.write(html)
print(f"Created fake_merchant.html for Order: {order_id}")
