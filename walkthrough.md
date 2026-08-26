# Package 05: State Machine Walkthrough

## What Changed
- **CaseWorkflowState**: Enriched the Domain model per architecture review. Modified `RecoveryCase` to own explicit `workflow_state` and `version` properties natively.
- **Migration & Concurrency**: Introduced `002_add_workflow_state.sql` which correctly normalizes existing state via a deterministic `CASE WHEN` clause and employs a transient trigger to defend against historically corrupted data. Rebuilt `RecoveryCaseRepository.save` to check expected vs database version counts via SQLite `rowcount`.
- **RecoveryStateMachine Engine**: Created the central execution logic in `recoverai/state_machine/engine.py` using `advance_workflow` and `close_case`. This acts as an orchestrator enforcing rules mapped directly from `ALLOWED_TRANSITIONS`, bypassing idempotency natively, and guarding terminal / unknown conditions safely.

## Validated Behavior
The state engine successfully executes transitions while protecting against blind retries of UNKNOWN events, illegal pipeline leaps, or race condition overwrites (utilizing the optimistic locking). All rules follow `docs/recovery_state_machine.md`.
