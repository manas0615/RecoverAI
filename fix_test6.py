import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("from recoverai.domain.money import CurrencyCode, Money", "from recoverai.domain.money import CurrencyCode, RevenueAmount")
content = content.replace("Money(100", "RevenueAmount(100")

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed Money to RevenueAmount.")
