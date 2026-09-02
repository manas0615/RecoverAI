import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("CaseStatus", "RecoveryCaseStatus")

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed CaseStatus to RecoveryCaseStatus.")
