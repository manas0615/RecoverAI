import re

with open("tests/unit/api/test_api_analyze.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("from recoverai.domain.case import RecoveryCase, RecoveryCaseId, RevenueSource, RecoveryCaseStatus, CaseWorkflowState", "from recoverai.domain.case import RecoveryCase, RecoveryCaseId, RevenueSource, RecoveryCaseStatus, CaseWorkflowState, RecoveryOutcomeType")
content = content.replace("workflow_state=CaseWorkflowState.CLOSED", "workflow_state=CaseWorkflowState.CLOSED,\n        outcome_type=RecoveryOutcomeType.RECOVERED")

with open("tests/unit/api/test_api_analyze.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed outcome_type.")
