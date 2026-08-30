# Failure Handling Validation

## Objective
Fix the failure logging flaw identified in the P2 audit where `action_service._trigger_n8n()` caught HTTP exceptions silently and logged `WORKFLOW_STARTED` regardless of success.

## Correction Implemented
1. Modified `_trigger_n8n()` to return `bool` indicating HTTP request success or failure.
2. Updated the caller for `payment-recovery` and `human-approval` to conditionally log:
   - `AuditEventType.WORKFLOW_STARTED`
   - `AuditEventType.WORKFLOW_TRIGGER_FAILED`
3. Created a regression unit test in `tests/unit/application/test_action_service_n8n.py`.

## Result
The test passes successfully. When the n8n HTTP trigger throws an exception, `WORKFLOW_TRIGGER_FAILED` is successfully audited to the case history.
