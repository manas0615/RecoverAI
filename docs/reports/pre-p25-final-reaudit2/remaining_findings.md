# PRE-P25 FINAL RE-AUDIT 2 — REMAINING FINDINGS

ID:
    REAUDIT-001

Severity:
    P2

Category:
    Orchestration Ledger Accuracy

Location:
    `recoverai/application/action_service.py` (lines 175-190)

Finding:
    Failed N8N invocation does not produce `WORKFLOW_TRIGGER_FAILED`. It logs a warning but proceeds to append `WORKFLOW_STARTED` to the database ledger anyway.

Evidence:
    `_trigger_n8n()` returns `None` and catches exceptions. The caller in `execute_action()` appends `AuditEventType.WORKFLOW_STARTED` unconditionally without checking the return value or network status.

Impact:
    The ledger incorrectly reports successful orchestration start even when network errors prevent the webhook from triggering.

Recommendation:
    Refactor `_trigger_n8n()` to return a boolean success flag, and write either `WORKFLOW_STARTED` or `WORKFLOW_TRIGGER_FAILED` conditionally.

Confidence:
    HIGH
