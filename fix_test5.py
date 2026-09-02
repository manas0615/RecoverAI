import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("RevenueSource.PAYMENT_LINK", "RevenueSource.PAYMENT")

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed RevenueSource.PAYMENT.")
