# Package 03 — Persistence Walkthrough

## Database Initialization
The initialization lives within `recoverai.persistence.connection.TransactionManager`. It uses `sqlite3.connect` dynamically parsing a `sqlite:///...` URL from `Settings`. 

## Connection Configuration
Every connection enforces standard protections immediately by executing `PRAGMA foreign_keys = ON;` and `PRAGMA journal_mode = WAL;`. `row_factory` is set to map rows to Python `dict`s.

## Migration Flow
The application bootstrapper runs `manager.run_migrations()`, which globs `.sql` files out of `recoverai/persistence/migrations/`. It checks `schema_migrations` to avoid double execution.

## Schema Structure
We constructed tables tracking 1-to-1 against pure domain model concepts. `001_initial.sql` defines `merchants`, `revenue_events`, `recovery_cases`, `recovery_actions` natively utilizing `TEXT` for identifiers.

## Domain → DB Mapping
The mappers live in `recoverai.persistence.mappers`. Datetimes call `.astimezone(timezone.utc).isoformat()`. `Money` converts directly to `event.amount.amount_minor` and `event.amount.currency.value`. 

## DB → Domain Mapping
The reconstruction parses UTC strings with `datetime.fromisoformat(val)` raising errors if naive time is presented. `row_to_money` natively maps tuples back into verified integer-only logic.

## Repository Usage
A caller initializes `RecoveryCaseRepository(conn)` passing an active transaction connection. The repository isolates SQL from the caller, simply executing `repo.save(case)`.

## Unit of Work
We provide `TransactionManager.transaction()` which executes a `BEGIN` statement natively and yields a connection. 

## Transaction Example
```python
with tm.transaction() as conn:
    RevenueEventRepository(conn).save(event)
    RecoveryCaseRepository(conn).save(case)
```
If an exception throws inside the context manager, it explicitly catches and invokes `conn.rollback()`.

## Duplicate Prevention
The repository captures `sqlite3.IntegrityError` if `UNIQUE(source_type, source_event_id)` is violated, re-raising a deterministic domain-level `DuplicateEntityError`. 

## Concurrency Handling
Idempotency is achieved by enforcing unique constraints within SQLite. For conflicting concurrent workflows attempting to mutate an action identically, the DB explicitly locks or throws a constraint failure, which we convert to a domain exception. 

## Error Handling
Corrupted database values (like `INVALID_ENUM` or `2026-01-01` missing timezone) explicitly fail via `ValueError` inside `mappers.py` instead of passing bad data upward.

## Test Database Isolation
`conftest.py` executes `tempfile.mkstemp(suffix=".db")` to guarantee every pytest execution writes isolated data to disk rather than fighting volatile `:memory:` database persistence across fixtures.

## Important Files
- `recoverai/persistence/connection.py`
- `recoverai/persistence/mappers.py`
- `recoverai/persistence/repositories/case.py`
