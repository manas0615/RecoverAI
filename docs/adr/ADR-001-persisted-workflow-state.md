# ADR-001 — Persisted Recovery Workflow State

## Status
Accepted

## Context
The architecture specification (`docs/recovery_state_machine.md`) defines a granular lifecycle for `RecoveryCase`, requiring transitions through states like `DETECTED`, `ENRICHING`, `ASSESSED`, `PLANNING`, `POLICY_REVIEW`, `WAITING_APPROVAL`, `EXECUTING`, and `VERIFYING`. However, the frozen P02 Domain Model (`RecoveryCase`) and P03 Persistence schema only track a high-level `status` (`OPEN`/`CLOSED`) and a terminal `outcome_type`. This created an architectural mismatch where pre-execution workflow states could not be durably tracked.

## Problem
A computed-state approach (deriving the workflow state purely from related entities like actions or assessments) is not acceptable because:
1. Pre-execution workflow states are not uniquely derivable from the frozen persisted facts (e.g., `DETECTED` vs. `ENRICHING` look identical in the DB).
2. It fails to reconstruct authoritative state deterministically across process restarts, risking idempotency violations (e.g., re-running enrichment).
3. It cannot support failure recovery for states like `WAITING_APPROVAL` or provide concurrency safety without a dedicated locking mechanism on the case.

## Decision
Persist `workflow_state` and `version` directly on `RecoveryCase`. 

## State Ownership
The `RecoveryCase` aggregate will own four distinct, non-overlapping state concepts:
- **`status`**: The high-level business container lifecycle (`OPEN` / `CLOSED`).
- **`workflow_state`**: The granular recovery workflow lifecycle (`DETECTED`, `ENRICHING`, etc.).
- **`outcome_type`**: The terminal business outcome (e.g., `RECOVERED`, `SUPPRESSED`).
- **`version`**: The optimistic concurrency token to prevent stale state overwrites.

## Alternatives Considered

### Computed State
**Rejected.** Cannot uniquely derive all states from existing facts. Fails restartability and idempotency guarantees for early workflow phases.

### Separate WorkflowStateRecord
**Rejected.** Creates a dangerous dual-source-of-truth anti-pattern. Requires complex cross-repository synchronization to maintain consistency between the `RecoveryCase` status and the separate workflow record.

### Persisted RecoveryCase Workflow State
**Accepted.** Modifying the domain model and schema to include `workflow_state` and `version` natively resolves the ambiguity, provides a single source of truth, and enables optimistic concurrency.

## Consequences
- Requires a backward-incompatible DB schema migration for P03.
- Requires updates to P02 domain classes.
- Provides mathematically deterministic failure recovery.

## Migration
A formal migration script must be provided to add `workflow_state` and `version` to the `recovery_cases` table. Existing local/demo databases must be migrated:
- `OPEN` cases will map to an appropriate active `workflow_state` depending on existing relations (e.g., if an action is EXECUTING, state is `EXECUTING`). Ambiguous mappings will fail migration explicitly to prevent corruption.
- `CLOSED` cases will map to a terminal workflow state corresponding to their `outcome_type`.

## Concurrency
A `version` integer will be added to `RecoveryCase`. State transitions will employ optimistic concurrency via atomic SQL updates `WHERE case_id = ? AND version = ?`. Stale workers will fail to overwrite newer workflow states.

## Failure Recovery
If a process crashes, the restarted worker will fetch the case and resume from the exact `workflow_state` seamlessly.

## Auditability
Every granular state transition can now be durably audited and logged because the state is explicit rather than heuristically computed.

## Implementation Impact
- **P02 (Domain):** Add `workflow_state: CaseWorkflowState` and `version: int` to `RecoveryCase`. Add the `CaseWorkflowState` enum.
- **P03 (Persistence):** Add columns to `recovery_cases` and update mappers. Implement optimistic locking in `RecoveryEventRepository`.
- **P05 (State Machine):** Implement the engine relying securely on these durable fields.
