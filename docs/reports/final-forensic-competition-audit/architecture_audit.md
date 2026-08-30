# 2. Architecture Audit

**Status:** Strong, Defensible, and Production-Oriented.

## State Machine Forensics
The domain state machine correctly enforces a fail-closed model.
- **Legal Transitions:** Observed in `recovery_cases` and `recovery_actions`.
- **Impossible States:** Impossible transitions (e.g., executing without authorization) are blocked by `PolicyEngine` invariants (Rule 1.3 blocks execution if an action is already active).
- **Stale State Protection:** Uses optimistic locking (`version` column) on `recovery_cases`. `UPDATE recovery_cases SET ... version = ? WHERE case_id = ? AND version = ?` ensures a concurrent thread cannot mutate a stale object.

## Concurrency and Race Conditions
- **Webhook Deduplication:** `idx_revenue_events_source` provides a strict `UNIQUE` constraint on `(source_type, source_event_id)`, guaranteeing webhooks are idempotently handled and rejected.
- **Concurrent Execution:** Database uniqueness `idx_recovery_actions_case_attempt` guarantees only a single `attempt_number` per action type exists per case, safely bouncing duplicate MCP calls.

## Error Propagation
Errors at the network boundary (`RazorpayAdapter`) are correctly typed into `PROVIDER_REJECTED`, `TIMEOUT_UNKNOWN`, and `NETWORK_UNKNOWN`. A timeout safely transitions the case into an `EXECUTION_UNKNOWN` / `UNCERTAIN_EXTERNAL_STATE` lock rather than falsely claiming success or quietly dropping the error.

## Database & Test Isolation
- **Isolation:** Tests via `pytest` run perfectly isolated via `test_db_path`.
- **Leakage:** Scripts in `scratch/` bypass the test config and can dangerously mutate the production `recoverai.db` due to direct `.env` fallback.

**Verdict:** The backend architectural scaffolding is the strongest, most competition-ready aspect of RecoverAI.
