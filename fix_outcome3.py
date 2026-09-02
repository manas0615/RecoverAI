import re

with open("tests/unit/api/test_api_analyze.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("CaseOutcomeType", "RecoveryOutcomeValue")

with open("tests/unit/api/test_api_analyze.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed RecoveryOutcomeValue.")
