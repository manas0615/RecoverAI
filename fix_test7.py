import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("from recoverai.domain.money import CurrencyCode, RevenueAmount, RevenueAmount", "from recoverai.domain.money import CurrencyCode, RevenueAmount, Money")
content = content.replace("RevenueAmount(RevenueAmount(", "RevenueAmount(Money(")
content = content.replace("from recoverai.domain.money import CurrencyCode, RevenueAmount\n    from recoverai.persistence", "from recoverai.domain.money import CurrencyCode, RevenueAmount, Money\n    from recoverai.persistence")
content = content.replace("amount_at_risk=RevenueAmount(100, CurrencyCode.INR),", "amount_at_risk=RevenueAmount(Money(100, CurrencyCode.INR)),")

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed Money/RevenueAmount.")
