# Package 05 — State Representation Reconciliation

## 1. Conflicting Specifications

The architecture specification (`docs/recovery_state_machine.md`) demands a highly granular, robust state machine to enforce the lifecycle of a `RecoveryCase`. It requires the system to distinguish fine-grained phases such as `DETECTED`, `ENRICHING`, `ASSESSED`, `PLANNING`, `POLICY_REVIEW`, `WAITING_APPROVAL`, `EXECUTING`, and `VERIFYING`.

However, the frozen P02/P03 domain model deliberately deferred workflow tracking. `RecoveryCase` simply records `status` (OPEN/CLOSED) and an eventual `outcome_type` (RECOVERED, NOT_RECOVERED, etc.). As a result, there is a fundamental conflict between the architectural need for durable, granular workflow states and the available persistence model.

## 2. Frozen P02/P03 State Representation

P02/P03 relies entirely on the presence of related entities and specific enums:
- **RecoveryCase:** `status` (OPEN/CLOSED) and `outcome_type` (RECOVERED, NOT_RECOVERED, SUPPRESSED, ESCALATED, EXPIRED, UNKNOWN).
- **RecoveryAction:** `status` (PROPOSED, AUTHORIZED, EXECUTING, EXECUTION_UNKNOWN, VERIFICATION_PENDING, VERIFIED_SUCCESS, VERIFIED_FAILURE, CANCELLED, ESCALATED).
- **Other Entities:** `RiskAssessment`, `InterventionPlan`, `PolicyDecision`, `VerificationRecord`.

## 3. Required Workflow State Representation

`docs/recovery_state_machine.md` mandates the ability to deterministically recover and enforce:
`DETECTED`, `ENRICHING`, `ASSESSED`, `PLANNING`, `POLICY_REVIEW`, `WAITING_APPROVAL`, `EXECUTING`, `VERIFYING`, `RECOVERED`, `NOT_RECOVERED`, `UNKNOWN`, `SUPPRESSED`, `ESCALATED`, `EXPIRED`, `CLOSED`.

## 4. Complete Derivation Matrix

| Workflow State | Persisted Facts Required | Can Current P02/P03 Represent Them? | Unique Derivation? | Persistent Across Restart? |
| --- | --- | --- | --- | --- |
| `DETECTED` | Case exists (`OPEN`). No assessments/actions. | Yes | NO (Ambiguous with ENRICHING) | NO |
| `ENRICHING` | Case exists (`OPEN`). Enrichment API called. | No (No enrichment record) | NO (Looks identical to DETECTED) | NO |
| `ASSESSED` | Case exists. `RiskAssessment`/`CauseAssessment` exist. | Yes | NO (Ambiguous with PLANNING) | NO |
| `PLANNING` | Candidate proposals being generated. | No (Stored only when complete) | NO (Looks identical to ASSESSED) | NO |
| `POLICY_REVIEW`| `RecoveryAction` exists as `PROPOSED`. | Yes | Yes (ActionStatus.PROPOSED) | Yes |
| `WAITING_APPROVAL`| Needs human authorization. | No explicit representation. | NO (Looks like PROPOSED/ESCALATED) | NO |
| `EXECUTING` | `RecoveryAction` is `EXECUTING`. | Yes | Yes | Yes |
| `VERIFYING` | `RecoveryAction` is `VERIFICATION_PENDING`. | Yes | Yes | Yes |
| `RECOVERED` | Case `CLOSED`, `outcome=RECOVERED`. | Yes | Yes | Yes |
| `NOT_RECOVERED`| Case `CLOSED`, `outcome=NOT_RECOVERED`. | Yes | Yes | Yes |
| `UNKNOWN` | Case `CLOSED`, `outcome=UNKNOWN`. | Yes | Yes | Yes |
| `SUPPRESSED` | Case `CLOSED`, `outcome=SUPPRESSED`. | Yes | Yes | Yes |
| `ESCALATED` | Case `CLOSED`, `outcome=ESCALATED`. | Yes | Yes | Yes |
| `EXPIRED` | Case `CLOSED`, `outcome=EXPIRED`. | Yes | Yes | Yes |
| `CLOSED` | Case `CLOSED`. | Yes | Yes | Yes |

## 5. Ambiguous States

The following workflow states cannot be uniquely derived from P02/P03 facts alone:
1. **DETECTED vs. ENRICHING:** Since P03 records no enrichment status, a process crash during enrichment looks identical to a newly created case upon restart.
2. **ASSESSED vs. PLANNING:** Planning relies on external AI/policy processing. If this crashes before an `InterventionPlan` is persisted, the system sees an `ASSESSED` case. The failure is invisible.
3. **POLICY_REVIEW vs. WAITING_APPROVAL:** P02 `ActionStatus` provides `PROPOSED`, but there is no mechanism to track if an action is awaiting human approval vs. a fast-path algorithmic policy review.

## 6. Restartability Analysis

A financial state machine must precisely resume execution upon restart.
Because states like `ENRICHING`, `PLANNING`, and `WAITING_APPROVAL` are ephemeral to the process memory in P02/P03:
- If a worker crashes during enrichment, the restarted system will assume the case was just `DETECTED` and re-run enrichment blindly (violating idempotency if enrichment mutates external state).
- If the system is `WAITING_APPROVAL`, a restart might lose the "waiting" context entirely, leaving the case stuck as `PROPOSED` with no notification to human operators.

**Restartability is NOT guaranteed for intermediate pre-execution workflow stages.**

## 7. Failure-Recovery Analysis

- **Case Workflow Crash (Pre-Execution):** Fails silently. Ambiguous rollback to previous logical checkpoint (`DETECTED` or `ASSESSED`).
- **Action Execution Crash:** Supported cleanly. `ActionStatus.EXECUTING` persists. The system can confidently move to `EXECUTION_UNKNOWN` or `VERIFICATION_PENDING`.
- **Approval Crash:** Not supported. State is lost.
- **Verification Crash:** Supported cleanly via `ActionStatus.VERIFICATION_PENDING`.

## 8. Concurrency Analysis

If Worker A reads an `OPEN` case with no actions, it derives the state as `DETECTED`/`ASSESSED`. Worker B simultaneously processes the case and persists an `InterventionPlan` (state = `POLICY_REVIEW`). Worker A, running on a stale projection, might attempt to generate a duplicate `InterventionPlan`. P03's DB schema does not have a comprehensive workflow-level concurrency token (like a state version number) on `RecoveryCase` to prevent stale transitions during the early workflow phases.

## 9. Options

### Option A — Computed State
Derive state from related entities (e.g., `if action.status == EXECUTING then case is EXECUTING`).
- **Correctness:** Low. Fails to distinguish pre-execution states (Enrichment, Planning, Approval).
- **Persistence Implications:** Zero. No DB changes.
- **Migration Implications:** None.
- **Complexity:** High cognitive load mapping missing states.
- **Failure Behavior:** Silent retries, lost approval requests, non-deterministic restarts.
- **Auditability:** Poor. We cannot log transitions like `DETECTED -> ENRICHING` safely.

### Option B — Persisted Workflow State
Modify P02 `RecoveryCase` to include a dedicated `workflow_state` enum column mapping directly to `docs/recovery_state_machine.md`, and a `version` column for optimistic locking.
- **Correctness:** High. Guaranteed authoritative state.
- **Persistence Implications:** Requires a DB schema migration (adding `workflow_state` to `recovery_cases`).
- **Migration Implications:** Minimal but real (updating P02 `RecoveryCase` and P03 mappers/schema).
- **Complexity:** Simple. Explicit state machine transitions `state = next_state`.
- **Failure Behavior:** Perfectly restartable. Resumes from exact state.
- **Auditability:** Complete. Every granular transition is verifiable.

### Option C — Hybrid / Projection
Store workflow tracking in an independent `WorkflowStateRecord` table without touching P02/P03's core `RecoveryCase`.
- **Correctness:** Moderate. The system now has two sources of truth (`RecoveryCase.status` vs `WorkflowStateRecord`).
- **Persistence Implications:** New P05 table/repo.
- **Migration Implications:** Additive only.
- **Complexity:** High. Requires syncing P03 `RecoveryCase` terminal states with the new workflow record atomically.
- **Failure Behavior:** Good, provided transactions span both records.
- **Auditability:** High.

## Final Decision

**Decision:** OPTION B — Persisted Workflow State
**Status:** APPROVED ARCHITECTURE AMENDMENT REQUIRED

## Why Computed State Was Rejected
Computed state cannot satisfy the restartability and idempotency guarantees required by a financial state machine. Because early workflow phases (like `ENRICHING` or `WAITING_APPROVAL`) leave no durable artifacts in P02/P03, a process crash causes the system to forget the current stage, leading to non-deterministic restarts and potential duplicate API actions.

## Why Separate WorkflowStateRecord Was Rejected
Introducing a secondary table for workflow state creates a dual-source-of-truth anti-pattern. Maintaining absolute consistency between `RecoveryCase.status` and `WorkflowStateRecord.state` would require complex coordination and invite corruption.

## New Authoritative State Model
The `RecoveryCase` aggregate acts as the sole authoritative owner of its state, utilizing four distinct, non-overlapping fields:
- `status`: Business lifecycle (`OPEN` / `CLOSED`)
- `workflow_state`: Granular workflow phase (e.g., `DETECTED`, `EXECUTING`)
- `outcome_type`: Terminal business outcome (e.g., `RECOVERED`)
- `version`: Optimistic concurrency token (integer)

## Required Changes to P02
`RecoveryCase` will be updated to include `workflow_state` and `version`. A new `CaseWorkflowState` Enum will be created reflecting the exact vocabulary in `docs/recovery_state_machine.md`.

## Required Changes to P03
The `recovery_cases` schema must be migrated to include `workflow_state` (TEXT) and `version` (INTEGER). Database mappers and repositories will be updated to persist these fields and enforce optimistic locking on updates.

## Required Changes to P05
The state machine engine will be built around these persistent, authoritative fields instead of attempting to compute the state heuristically.

## Migration Requirements
A formal migration script must be executed. Existing `OPEN` cases must be carefully mapped to their corresponding `workflow_state` based on related facts. If a case is ambiguous, the migration must fail rather than invent data. `CLOSED` cases will map to their terminal counterpart based on their `outcome_type`.

## Concurrency Requirements
Updates to `RecoveryCase` will enforce optimistic concurrency checking (`WHERE version = ?`). This guarantees that a stale worker reading an `OPEN` case will fail to overwrite the database if another worker has already advanced the workflow state.

## Testing Requirements
The implementation will require tests proving that:
- Optimistic locking successfully blocks stale transitions.
- The DB schema migration runs flawlessly and handles ambiguous legacy state securely.
- All legal and illegal state transitions respect the new persisted `workflow_state` field.
