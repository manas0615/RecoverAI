# Package 05: State Machine Walkthrough

## What Changed
- **CaseWorkflowState**: Enriched the Domain model per architecture review. Modified `RecoveryCase` to own explicit `workflow_state` and `version` properties natively.
- **Migration & Concurrency**: Introduced `002_add_workflow_state.sql` which correctly normalizes existing state via a deterministic `CASE WHEN` clause and employs a transient trigger to defend against historically corrupted data. Rebuilt `RecoveryCaseRepository.save` to check expected vs database version counts via SQLite `rowcount`.
- **RecoveryStateMachine Engine**: Created the central execution logic in `recoverai/state_machine/engine.py` using `advance_workflow` and `close_case`. This acts as an orchestrator enforcing rules mapped directly from `ALLOWED_TRANSITIONS`, bypassing idempotency natively, and guarding terminal / unknown conditions safely.

## Implementation Details

The implementation flows through the layers precisely:
1. **Domain**: `RecoveryCase` initializes or mutates its in-memory `version` and `workflow_state` under strict domain invariant checks inside `__post_init__` and `advance_workflow`.
2. **P03 Persistence**: `RecoveryCaseRepository.save()` receives the domain entity. It pulls the old in-memory version, calculates `old_version + 1`, and executes an optimistic update `WHERE case_id = ? AND version = old_version`. 
3. **P05 State Machine**: `RecoveryStateMachine` orchestrates this by accepting semantic business commands. It validates the intent against allowed transitions.
4. **Transaction**: The engine opens a `TransactionManager.transaction()` block. Within the block, it fetches the case using `RecoveryCaseRepository.get`, validates the transition, mutates the domain state, and attempts a `save()`.
5. **Optimistic Version Check**: If another process modified the row concurrently, the `save()` query's `rowcount` will return `0`. This raises a `StaleStateTransitionError` which immediately bubbles up, aborting and automatically rolling back the SQLite transaction cleanly.

## Package 16: Frontend / Stitch UI
- Initialized a React + Vite + TypeScript frontend.
- Applied enterprise design systems via Stitch MCP (Dark-First, Deep Navy).
- Created the Dashboard and Tri-Fold Case Detail components.
- Integrated directly with the existing P15 Backend API over Vite Proxy.
