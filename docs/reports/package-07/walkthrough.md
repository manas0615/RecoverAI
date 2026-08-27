# Package 07 — Policy Engine Walkthrough

## 1. Policy Input
The `PolicyEngine.evaluate()` function takes explicit, typed domain inputs: `PolicyContext`, `RecoveryCase`, `InterventionPlan`, `List[RecoveryAction]` (for history), and an optional `CauseAssessment`. 

## 2. PolicyContext
An immutable configuration struct `PolicyContext` holds the configuration for evaluation:
- `policy_version`
- `current_time`
- `max_attempts_per_case`
- `high_value_threshold`
This removes implicit or ambient state configuration (like wall-clock time) out of the engine, ensuring determinism.

## 3. Rule Evaluation Pipeline
Evaluations flow sequentially through 4 core segments in `PolicyEngine`:
1. Missing action fail-closed
2. Hard System Safety Invariants
3. Systemic Degradation context rules
4. Merchant-Configurable Policies

## 4. Rule Precedence
Conflicts are resolved by sequential execution order. System safety rules (e.g. `CASE_TERMINAL`) evaluate before merchant overrides (e.g. `HIGH_VALUE_ACTION`), meaning safety logic inherently overrides merchant config logic. For instance, a high-value transaction on a terminal case resolves to `CASE_TERMINAL` (`DENY`), rather than merely `HIGH_VALUE_ACTION` (`ESCALATE`).

## 5. Safety Gates
- Terminal Case Check (`status == CLOSED`) -> `DENY`
- Unknown External State (`EXECUTION_UNKNOWN`) -> `DENY`
- Duplicate Active Action (`PROPOSED/AUTHORIZED/EXECUTING/VERIFICATION_PENDING`) -> `DENY`

## 6. Decision Generation
The engine is purely functional, returning an immutable `PolicyDecision` object capturing the decision value (`APPROVE`, `DENY`, `SUPPRESS`, `ESCALATE`), matching rules, and the `policy_version`.

## 7. Reason Codes
A mapped list of strings inside `PolicyDecision`, such as `UNCERTAIN_EXTERNAL_STATE`, `ATTEMPT_LIMIT_REACHED`, and `HIGH_VALUE_ACTION`.

## 8. Unknown / Revalidation
Matches `SAFETY_002`. Handled by checking if ANY action of the requested type exists in `EXECUTION_UNKNOWN`. Produces `DENY` (`UNCERTAIN_EXTERNAL_STATE`).

## 9. Attempt Limits
Counts only past financially mutating actions (e.g., `CREATE_PAYMENT_LINK`).

## 10. High-Value Approval
Checks `case.amount_at_risk` against `context.high_value_threshold`. Requires exact currency matching using `CurrencyCode`.

## 11. Systemic Degradation
Blocks financial mutations when `cause.category == "SYSTEMIC_DEGRADATION"`, returning `SUPPRESS`. Allows non-mutating actions (`WAIT`).

## 12. AI Boundary
AI models return an `InterventionPlan` (Action Selection) and `CauseAssessment` (Reasoning). The Policy Engine treats these as untrusted inputs and processes them through rules. The AI cannot "force" an action.

## 13. P05 Boundary
The Policy Engine evaluates state but DOES NOT update the `RecoveryCase` workflow state. Application orchestration leverages the output `PolicyDecision` to trigger any case workflow changes.

## 14. Persistence Boundary
Persistence uses `PolicyDecisionRepository.save()`. Evaluation and Saving are uncoupled; the engine generates a snapshot, and the app decides when to commit it to the DB using `TransactionManager`.

## 15. Failure Handling
Safely returns `ESCALATE` (e.g., `CURRENCY_MISMATCH_IN_POLICY`) when input facts contradict (e.g., wrong currencies for threshold evaluations).

## 16. Important Files
- `recoverai/policy/engine.py`: Defines context, pipeline, and decision builders.
- `recoverai/persistence/repositories/policy.py`: Repository implementation.
- `tests/unit/policy/test_policy_engine.py`: Extensive policy test suite.

## 17. Test Coverage
Extensive unit tests mapping all required constraints, threshold boundary tests, conflict precedence, and AI bypass tests.
