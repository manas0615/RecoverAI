# Package 03 — Persistence

## Status

IMPLEMENTED / VERIFIED

## Objective

Build the persistence layer to accurately store and retrieve the pure P02 domain model utilizing standard library SQLite without an ORM, and providing transactional boundaries.

## Persistence Architecture

Standard library `sqlite3` driver. The dependency flows from `recoverai.persistence` to `recoverai.domain`. 

## Schema

- `schema_migrations`: Tracks sequentially applied version scripts.
- `merchants` / `customers`: Store identity and relational hierarchy.
- `revenue_events`: The immutable, deduplicated financial event logs.
- `recovery_cases`: Mutable aggregates tracking current risk and case outcome.
- `case_source_events`: Junction mapping many-to-many relationship of a case utilizing multiple events.
- `recovery_actions`: Individual logical/execution attempts referencing policies.
- `policy_decisions` & `verification_records`: Auth logs and success confirmations.

## Domain Mapping

- **Domain Type -> DB Representation:**
  - `Money`: 2 columns (INTEGER `amount_minor`, TEXT `currency`). 
  - `Probability`: REAL `recovery_probability` (validated strictly on load).
  - Timezone Aware Datetime: ISO8601 UTC string (e.g. `2026-08-26T16:00:00+00:00`).
  - Typed Enums: Persisted using `.value` (TEXT). Unknown enums throw explicit ValueError on reconstruction.
  - JSON structures: Unstructured rules/metadata serialized via `json.dumps`.

## Repository Interfaces

We explicitly implemented:
- `RevenueEventRepository`
- `RecoveryCaseRepository`
- `RecoveryActionRepository`

These provide domain-level abstractions `repo.save(domain_entity)` and `repo.get(typed_id)`.

## Transaction Strategy

A `TransactionManager` exposes a context manager `transaction()` that yields a raw connection executing within a `BEGIN ... COMMIT/ROLLBACK` block, guaranteeing that operations like saving a case and linking its event references happen atomically.

## Concurrency Strategy

Duplicate prevention and concurrency safety are provided through database uniqueness constraints, SQLite transaction semantics, and conditional writes where applicable.
The system does not build its own state machine; it relies on foreign keys and compound unique keys (e.g., `(case_id, action_type, attempt_number)`) and `(idempotency_key)` to deterministically fail stale or duplicate workflows with `DuplicateEntityError`.

## Uniqueness Constraints

- `idx_revenue_events_source`: `UNIQUE(source_type, source_event_id)` where `source_event_id IS NOT NULL`. (Protects Razorpay webhooks).
- `idx_recovery_actions_idempotency`: `UNIQUE(idempotency_key)` where `idempotency_key IS NOT NULL`. (Protects logical action retries globally).

## Migration Strategy

Explicit `.sql` scripts applied sequentially via `connection.py:TransactionManager.run_migrations()`.

## Error Mapping

`sqlite3.IntegrityError` mapped securely to `DuplicateEntityError`.

## Tests

Extensive `pytest` fixtures deploying an isolated temporary-file SQLite database. Tested money serialization, constraint bounds, corrupted enums (fallback exceptions), and explicit rollback transactions.

## Files Created

- `recoverai/persistence/connection.py`
- `recoverai/persistence/exceptions.py`
- `recoverai/persistence/mappers.py`
- `recoverai/persistence/repositories/action.py`
- `recoverai/persistence/repositories/case.py`
- `recoverai/persistence/repositories/event.py`
- `recoverai/persistence/migrations/001_initial.sql`
- `tests/unit/persistence/test_persistence.py`
- `tests/unit/persistence/test_corrupt.py`
- `tests/unit/persistence/conftest.py`

## Files Modified

None outside of `recoverai/persistence/` or `tests/unit/persistence/`.

## Dependencies

None added. Pure standard-library Python.

## Known Limitations

- No explicit schema rollback scripts (down-migrations) are provided for MVP.

## Unexpected Findings

- Using `:memory:` for pytest tests natively resets the schema on each new connection open, so `conftest.py` implements an explicit temporary file generation to support shared connection testing without memory wipes.

## Git Commit SHAs

Implementation Commit: `c738608`
Documentation Commit: (See latest)
