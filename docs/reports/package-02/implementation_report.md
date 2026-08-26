# Package 02 — Domain Model

## Status

IMPLEMENTED / VERIFIED

## Scope

This package establishes the explicit, infrastructure-independent Python domain model that forms the core of the RecoverAI system, covering value objects, entity relationships, invariant tracking, and strict identifiers as requested in `docs/domain_model.md`.

## Domain Specification Mapping

- **Money & RevenueAmount**
  - *Architecture source:* `docs/domain_model.md` Sections 7, 8
  - *Implementation type:* `dataclasses.dataclass(frozen=True)` wrapper
  - *Purpose:* Store integer minor units and explicit currency, rejecting float instantiation and cross-currency arithmetic securely.

- **Merchant**
  - *Architecture source:* `docs/domain_model.md` Section 5
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* Owns business identity; holds configuration references.

- **Customer**
  - *Architecture source:* `docs/domain_model.md` Section 6
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* Lightweight customer representation maintaining strictly decoupled PII (only `contact_reference`).

- **RevenueEvent**
  - *Architecture source:* `docs/domain_model.md` Section 11 & `docs/event_model.md`
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* Immutable representation of a historical source observation, completely independent from `RecoveryCase` creation.

- **RecoveryCase**
  - *Architecture source:* `docs/domain_model.md` Section 14
  - *Implementation type:* `dataclasses.dataclass`
  - *Purpose:* Central aggregate root. Represents a mutable revenue opportunity that transitions securely based on intrinsic methods rather than raw setters.

- **RiskAssessment & CauseAssessment**
  - *Architecture source:* `docs/domain_model.md` Sections 18, 19
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* Explanatory snapshots tied explicitly to `EvidenceReference`, proving AI determinations are drawn from facts.

- **InterventionCandidate & InterventionPlan**
  - *Architecture source:* `docs/domain_model.md` Sections 22, 24
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* Represents non-authoritative candidate strategies before execution.

- **PolicyDecision**
  - *Architecture source:* `docs/domain_model.md` Section 26
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* A purely deterministic authorization snapshot blocking unauthorized executions securely.

- **RecoveryAction**
  - *Architecture source:* `docs/domain_model.md` Section 28
  - *Implementation type:* `dataclasses.dataclass`
  - *Purpose:* Tracks exactly one execution attempt tied to an idempotency identity and an explicit Case linkage.

- **VerificationRecord**
  - *Architecture source:* `docs/domain_model.md` Section 32
  - *Implementation type:* `dataclasses.dataclass(frozen=True)`
  - *Purpose:* Persists explicitly resolved state (SUCCESS, FAILURE, UNKNOWN) as defined by an execution verification check.

## Domain Objects

- `Merchant`: Represents business context. 
- `Customer`: Minimal representation of a human participant.
- `RevenueEvent`: Represents historical facts and source mapping (e.g. `PAYMENT_FAILED`).
- `RecoveryCase`: Main Aggregate Root mapping risks to opportunities.
- `RecoveryAction`: Specific action attempt instance guaranteeing policy tracking.
- `PolicyDecision`: Snapshot of deterministic permission.
- `VerificationRecord`: Validated outcome (SUCCESS, FAILURE, UNKNOWN).
- `RiskAssessment` & `CauseAssessment`: Predictive state entities mapping models.
- `InterventionCandidate` & `InterventionPlan`: Strategy proposal entities.

## Value Objects

- `Money`: Validates integer arithmetic, matching currency, and rejects floating points to prevent financial corruption.
- `RevenueAmount`: A wrapper for `Money` enforcing non-negative properties.
- `Probability`: Validates native boundaries (`[0.0, 1.0]`) and ensures explicit, non-NaN/Inf semantics. 
- `EvidenceReference`: Maps an explicitly identified domain fact to a model's prediction.

## Identifier Strategy

**Strategy Chosen:** Extensible Immutable Data Class Wrappers (`_DomainId`).

Every core business ID (`MerchantId`, `RecoveryCaseId`, etc.) is represented as a strongly-typed `dataclass(frozen=True)` inheriting a custom class verifying `value`. 
- **Reason:** Provides both strict static type separation (`MerchantId` != `CustomerId`) during parameter typing and rigorous runtime protections throwing exceptions when given empty strings, whitespace, or invalid types.

## State Types

- `CurrencyCode` (`INR`, `USD`, `EUR`, `GBP`)
- `RevenueEventType`
- `EventSourceType` 
- `RecoveryCaseStatus` (`OPEN`, `CLOSED`)
- `RevenueSource`
- `RecoveryOutcomeValue` (`RECOVERED`, `NOT_RECOVERED`, `UNKNOWN`, etc.)
- `ActionType`
- `ActionStatus` (`PROPOSED`, `AUTHORIZED`, `EXECUTING`, `VERIFICATION_PENDING`, `VERIFIED_SUCCESS`, etc.)
- `PolicyDecisionValue` (`APPROVE`, `DENY`, `SUPPRESS`, etc.)
- `VerifiedState` (`SUCCESS`, `FAILURE`, `UNKNOWN`)
- `AnalysisType`
- `CandidateStatus`

## Aggregate Boundary

**RecoveryCase** owns the responsibility of governing risk analysis against a specific opportunity but does NOT own the `RevenueEvent` existence. It explicitly tracks its references (`source_event_ids`) and validates basic logical transitions internally without attempting to act as an execution machine.

## Event Lifecycle

The `RevenueEvent` completely avoids circular lifecycle logic. It is instantiated immutably based on external conditions (e.g. webhook) completely unaware of cases. `RecoveryCase` explicitly builds on top of an already-minted set of event references.

## State-Machine Boundary

I explicitly deferred the heavy workflow state transitions (detect -> assess -> decide -> execute) to Package 05. The domain classes expose local validation against physically impossible invariants (e.g., executing a closed case) but are deliberately not coupled to complex workflow transition graphs.

## Files Created

- `recoverai/domain/__init__.py`
- `recoverai/domain/action.py`
- `recoverai/domain/assessment.py`
- `recoverai/domain/case.py`
- `recoverai/domain/customer.py`
- `recoverai/domain/event.py`
- `recoverai/domain/evidence.py`
- `recoverai/domain/identifiers.py`
- `recoverai/domain/merchant.py`
- `recoverai/domain/money.py`
- `recoverai/domain/plan.py`
- `recoverai/domain/policy.py`
- `recoverai/domain/verification.py`
- `tests/unit/domain/test_action.py`
- `tests/unit/domain/test_architecture.py`
- `tests/unit/domain/test_case.py`
- `tests/unit/domain/test_event.py`
- `tests/unit/domain/test_identifiers.py`
- `tests/unit/domain/test_misc.py`
- `tests/unit/domain/test_money.py`

## Files Modified

None (outside of core domain).

## Dependencies

None added. Pure pythonic infrastructure built atop existing standard libraries. Pydantic intentionally avoided per constraints.

## Known Limitations

- `RecoveryAction.idempotency_key` natively uses `str`. It defers explicit formatting requirements (e.g. compound action uniqueness) to the execution handler as different APIs (Razorpay) have differing character limits/requirements.

## Unexpected Findings

None. Implemented successfully.

## Git Commit

`1f33449`
