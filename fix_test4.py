import re

with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("from recoverai.domain.case import RecoveryCase, RecoveryCaseId, RecoveryCaseStatus", "from recoverai.domain.case import RecoveryCase, RecoveryCaseId, RecoveryCaseStatus, RevenueSource")
content = content.replace('source_event_ids=[RevenueEventId("ev_1")],', 'source_event_ids=[RevenueEventId("ev_1")],\n            revenue_source=RevenueSource.PAYMENT_LINK,')

with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed revenue_source.")
