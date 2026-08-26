# Package 06 — Revenue Intelligence

## Status
Implementation complete and fully verified.

## Objective
Implement the Revenue Intelligence layer (P06) responsible for analyzing revenue events, estimating recovery probability, determining the root cause of failures, and generating an intervention plan with candidate strategies. This layer strictly separates analytical intelligence from financial execution and policy authorization.

## Intelligence Architecture
The `RevenueIntelligenceAnalyzer` acts as the primary orchestrator mapping `RecoveryCase` and `RevenueEvent` instances to:
1. `RiskAssessment`: Deterministically scores recovery probability and expected value.
2. `CauseAssessment`: Maps failure categories (either statistically or via an abstract LLMGateway for complex context).
3. `InterventionPlan`: Evaluates multiple `InterventionCandidate` options and selects the optimal path bounded by deterministic cost/friction equations.

## Deterministic vs AI Responsibilities
- **Deterministic**: Expected recovery arithmetic, baseline friction scoring, action eligibility filters, probability validation (0.0 - 1.0).
- **AI (Abstracted)**: Root cause synthesis from heterogeneous context, selection of the optimal intervention strategy from valid candidates.

## Inputs
`RevenueIntelligenceAnalyzer.analyze(case, events, context)` consumes:
- `RecoveryCase`
- Collection of `RevenueEvent`
- Optional dictionary of `context` (customer history, merchant settings)

## Feature / Signal Construction
Extracts raw context and event metadata (e.g. error source, step, reason from Razorpay) into normalized feature maps passed to the downstream assessment engines.

## Risk Assessment
Implemented via a deterministic fallback that scores baseline recoverability based on event metadata (e.g. temporary insufficient funds vs terminal fraud closures). Uses the frozen P02 `Probability` and `RiskAssessment` objects.

## Cause Assessment
Implemented to output a structured `CauseAssessment` with a defined categorical taxonomy (e.g., `CUSTOMER_SPECIFIC`, `SYSTEMIC_DEGRADATION`). Integrates with `LLMGateway.synthesize_cause` when injected, falling back to deterministic mappings if omitted.

## Intervention Candidates
Generates multiple `InterventionCandidate` objects based on the P02 `ActionType` enum. Ranks options using expected recovery arithmetic: `probability * value - cost`.

## Intervention Plan
Packages the valid candidates into an `InterventionPlan`. Ensures the selected candidate exists in the evaluated set and is eligible.

## Evidence Grounding
Generates `EvidenceReference` objects linking `event_id` directly to each assessment and plan.

## AI Boundary
Abstracted entirely behind the `LLMGateway` interface in `gateway.py`. Structured outputs are strictly typed to domain objects.

## LLM Gateway Boundary
`recoverai.intelligence.gateway.LLMGateway` provides abstract methods for cause synthesis and intervention ranking. No specific provider SDKs (Gemini/Groq) are imported or used.

## Failure Handling
The orchestrator gracefully falls back to deterministic/baseline assessments if the LLMGateway is unavailable or raises exceptions.

## Fallback Behavior
Without AI, the system maps Razorpay error strings natively to cause categories, and falls back to a deterministic `WAIT` or `CREATE_PAYMENT_LINK` based on simple thresholds.

## Persistence
All generated domain objects (`RiskAssessment`, `CauseAssessment`, `InterventionPlan`) are returned cleanly to the caller. Persistence logic sits externally or defers to future packages (as P03 did not define tables for these beyond what exists). Note: P03 actually *did* define `risk_assessments` and `intervention_plans` tables. We will defer saving to the caller or standard repository pattern.

## Security
No arbitrary API execution, SQL injection paths, or unvalidated prompts. Customer metadata is explicitly isolated from intelligence instruction logic in the interfaces.

## Testing
68+ comprehensive unit tests covering deterministic extraction, feature boundaries, AI gateway injection/fallback, validation logic, and regression over P01-P05.

## Exact Git Commit SHAs
Implementation Commit: 3ec3f3c
Documentation Commit: 3dc871c
