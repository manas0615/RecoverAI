import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("RevenueRevenueEventId", "RevenueEventId")
content = content.replace("Currency", "CurrencyCode")
content = content.replace("CurrencyCodeCode", "CurrencyCode")

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed Currency and EventId.")
