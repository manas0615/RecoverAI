# Package 07 — Policy Engine

## Status
VERIFIED

## Policy Architecture
The Policy Engine acts as the definitive authorization boundary between AI recommendations (P06) and execution (P08). It is 100% deterministic, side-effect-free in its evaluation, and generates an immutable `PolicyDecision` snapshot using context inputs and rule precedence.

## Hard Safety Invariants
1. `CASE_TERMINAL`: No evaluation if the case is `CLOSED`.
2. `UNCERTAIN_EXTERNAL_STATE`: Blocks execution if ANY prior action of the same type is `EXECUTION_UNKNOWN`.
3. `DUPLICATE_ACTIVE_RECOVERY_ACTION`: Blocks execution if an action of the same type is currently `PROPOSED`, `AUTHORIZED`, `EXECUTING`, or `VERIFICATION_PENDING`.
4. `ACTION_NOT_ELIGIBLE`: Must be a supported `ActionType`.

## Merchant-Configurable Rules
- **Attempt Limits**: Configurable max attempts per case.
- **High-Value Approvals**: Configurable threshold (e.g. 100,000 INR) triggering an `ESCALATE` state.

## PolicyContext
The evaluation is configured by a typed `PolicyContext` containing `policy_version`, `current_time`, `max_attempts_per_case`, and `high_value_threshold`. Defaults are explicit and versioned. 

## Rule Precedence
1. `CASE_TERMINAL` (DENY)
2. `UNCERTAIN_EXTERNAL_STATE` (DENY)
3. `DUPLICATE_ACTIVE_RECOVERY_ACTION` (DENY)
4. `ACTION_NOT_ELIGIBLE` (DENY)
5. `SYSTEMIC_DEGRADATION` (SUPPRESS)
6. `ATTEMPT_LIMIT_REACHED` (SUPPRESS)
7. `CURRENCY_MISMATCH_IN_POLICY` (ESCALATE)
8. `HIGH_VALUE_ACTION` (ESCALATE)
9. `POLICY_APPROVED` (APPROVE)

## Decision Values
`APPROVE`, `DENY`, `SUPPRESS`, `ESCALATE`, `REVALIDATE`.

## Reason Codes
Mapped string reason codes returned in `matched_rules` and `reason_codes`. (e.g., `UNCERTAIN_EXTERNAL_STATE`).

## Attempt Semantics
Counted for financially mutating actions (`CREATE_PAYMENT_LINK`, `SEND_PAYMENT_LINK_NOTIFICATION`, `PAYMENT_LINK_REMINDER`). Excludes `WAIT`, `SUPPRESS`, `ESCALATE`.

## High-Value Semantics
Threshold is provided in `PolicyContext` using `RevenueAmount`. Currency must exactly match `case.amount_at_risk.currency`. If not, it fails closed (`ESCALATE`).

## UNKNOWN Handling
Follows `SAFETY_002` (No blind retry after `EXECUTION_UNKNOWN`). Handled as `UNCERTAIN_EXTERNAL_STATE`.

## Systemic Degradation
Uses `CauseAssessment.category == "SYSTEMIC_DEGRADATION"`. Disables financial mutations by triggering `SUPPRESS`.

## Action Eligibility
Syntactically valid ActionTypes are verified. Eligibility is checked explicitly against the authorized ActionTypes.

## Policy Versioning
Uses `PolicyContext.policy_version` and is snapped into `PolicyDecision.policy_version`.

## AI Separation
No direct LLM calls. The AI constructs an `InterventionPlan` and `CauseAssessment`, which are passed as purely deterministic inputs into the Engine. AI confidence cannot bypass Policy logic.

## P05 State-Machine Boundary
P07 evaluates policy and returns a `PolicyDecision`. It does NOT trigger `RecoveryCase` transitions internally.

## Persistence
`PolicyDecision` is saved into SQLite via `PolicyDecisionRepository` reusing the P03 `TransactionManager`.

## Determinism
100% deterministic. Testable offline. Time is injected via `PolicyContext.current_time`.

## Failure Handling
Any invalid type, missing field, or currency mismatch escalates or denies safely.

## Security
No dynamic rule generation or DSL. No implicit inputs.

## Tests
Complete matrix of precedence conflicts tested in `tests/unit/policy/test_policy_engine.py`.

## Files Created
- `recoverai/policy/engine.py`
- `recoverai/persistence/repositories/policy.py`
- `tests/unit/policy/test_policy_engine.py`

## Files Modified
- `recoverai/persistence/repositories/__init__.py`

## Dependencies
P02 Domain, P03 Persistence.

## Known Limitations
No API/frontend yet. Revalidation transitions require full workflow layer logic to execute properly.

## Unexpected Findings
None.

## Exact Git Commit SHAs
Implementation Commit: 15bb9ed
