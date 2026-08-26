# Package 02 — Implementation Walkthrough

## 1. Entry Points

The domain entities are exposed through the clean `recoverai.domain` package root (`recoverai/domain/__init__.py`), making standard imports extremely clear (e.g., `from recoverai.domain import RecoveryCase, Money, CurrencyCode, MerchantId`).

## 2. Domain Structure

- **identifiers:** (`recoverai/domain/identifiers.py`) Implements a structural `_DomainId` python class wrapping a string, rigorously tracking identities as separated runtime validation classes (e.g., `RevenueEventId` != `CustomerId`).
- **money:** (`recoverai/domain/money.py`) The absolute financial truth representation. Stores amounts strictly as `int`, executing custom overloads (`__add__`, `__sub__`, `__eq__`) to prevent cross-currency collisions.
- **events:** (`recoverai/domain/event.py`) `RevenueEvent` accurately wraps observed immutable facts linking `EventSourceType` to raw financial observations.
- **case:** (`recoverai/domain/case.py`) `RecoveryCase` is the central aggregate instance tracking `status` and `outcome_type` natively with strict domain logic restrictions (e.g., `close()`).
- **actions:** (`recoverai/domain/action.py`) `RecoveryAction` dictates an attempt. Tracks transition methods `authorize`, `begin_execution`, and `record_verification` to keep mutable updates local.
- **assessments:** (`recoverai/domain/assessment.py`) Maps deterministic `Probability` records to `RiskAssessment` and `CauseAssessment` representations.
- **planning:** (`recoverai/domain/plan.py`) Maps `InterventionCandidate` objects into a single explicit `InterventionPlan`.
- **policy:** (`recoverai/domain/policy.py`) Contains `PolicyDecision`, an immutable snapshot mapping a specific case action attempt to an `APPROVE`, `DENY`, or `SUPPRESS` result.
- **verification:** (`recoverai/domain/verification.py`) `VerificationRecord` securely represents the observed result from an external webhook/manual entry mapping explicitly to `SUCCESS`, `FAILURE`, or `UNKNOWN`.

## 3. Object Relationships

- `RecoveryCase` holds a `set[RevenueEventId]` maintaining external relationship mappings without enforcing strict lifecycle instantiation hierarchies.
- `RecoveryAction` binds to `RecoveryCaseId` (identifying the parent case) and `PolicyDecisionId` (enforcing authorization explicitly tracked).
- `VerificationRecord` binds directly to `RecoveryActionId`.
- Analytic structures (`InterventionPlan`, `RiskAssessment`) point strictly back to `RecoveryCaseId` and wrap instances of `EvidenceReference`.

## 4. Invariants

- **Integer Money:** `Money` structurally validates `isinstance(self.amount_minor, int)` and throws exception against floating-point arguments natively.
- **Currency Mismatch:** `Money`'s `__add__` structurally asserts `self.currency == other.currency`.
- **Identifier Validation:** `_DomainId.__post_init__` verifies inputs are non-empty strings.
- **Timezone-Aware Timestamps:** Everywhere a `datetime` is expected, `tzinfo` guarantees are executed via `__post_init__` natively throwing exceptions.
- **Event Immutability:** `RevenueEvent` natively uses `dataclasses.dataclass(frozen=True)` which traps internal field reassignment natively producing a `FrozenInstanceError`.
- **RecoveryCase Safeguards:** Requires minimum initial `source_event_ids`. Requires an explicit `recovered_amount` when calling `close(RecoveryOutcomeValue.RECOVERED, ...)`
- **RecoveryAction Safeguards:** Only explicitly `PROPOSED` objects can be `authorize()`d.
- **UNKNOWN Verification:** Native `VerifiedState.UNKNOWN` representation exists cleanly independent of failure states in `VerificationRecord`.

## 5. Mutability

- **Immutable:** Value objects (`Money`, `Probability`, `EvidenceReference`) and historical facts (`RevenueEvent`, `VerificationRecord`, `PolicyDecision`) are fundamentally structured using `frozen=True` preventing mutation mathematically.
- **Mutable Lifecycle Objects:** `RecoveryCase` and `RecoveryAction` are allowed to drift through statuses (`OPEN`/`CLOSED`, `PROPOSED`/`EXECUTING`), but this drift is explicitly controlled via rigid class methods checking intrinsic pre-conditions rather than external dict setters.

## 6. Dependency Boundary

The entire system requires zero infrastructure imports. `test_architecture.py` dynamically scans the domain directory natively executing AST analysis, guaranteeing packages like `pydantic`, `fastapi`, and `sqlalchemy` cannot leak into core domain classes.

## 7. Package 05 Boundary

We intentionally omitted:
- State execution engines mapping polling loops or transitioning.
- Broad transition validity matrices that move a case from initial detection toward policy verification natively. P02 only provides the objects, letting P05 drive the transitions.

## 8. Test Coverage

- `test_money.py` confirms integer bounds checking, `CurrencyCode` mismatch exceptions (`test_money_currency_mismatch`), and strict float rejection (`test_money_rejects_floats`).
- `test_identifiers.py` enforces explicit runtime mismatch errors when blank text inputs are presented (`test_identifier_rejects_empty`).
- `test_event.py` runs `test_revenue_event_rejects_naive_datetime` ensuring local clocks can't leak into database serialization logic.
- `test_case.py` proves that `case.close(RecoveryOutcomeValue.RECOVERED...)` produces deterministic errors when missing financial evidence (`test_recovery_case_close_requires_amount_when_recovered`).
- `test_architecture.py` iterates internal python AST trees catching forbidden import leaks (`test_domain_has_no_infrastructure_imports`).
