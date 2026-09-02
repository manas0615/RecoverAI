import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("amount=RevenueAmount(10000, CurrencyCode.INR),", "amount=RevenueAmount(Money(10000, CurrencyCode.INR)),")

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed RevenueAmount(10000).")
