# Package 06 — Revenue Intelligence Walkthrough

## 1. Intelligence Entry Point
The entry point is `recoverai.intelligence.analyzer.RevenueIntelligenceAnalyzer`. It orchestrates the analysis of a `RecoveryCase` and its associated `RevenueEvent` instances. 

## 2. Input Context
The analyzer consumes the `RecoveryCase`, a list of `RevenueEvent` objects, and an optional `context` dictionary containing external signals such as `active_downtime` and `customer_failure_count`.

## 3. Feature / Signal Construction
Inside `_extract_features()`, raw events and context are mapped into simple signals like `has_systemic_signal` and `customer_failure_count`. This isolates the rest of the engine from needing to parse arbitrary JSON payloads repeatedly.

## 4. Risk Analysis
The `_assess_risk()` function applies a deterministic baseline model. It assigns a baseline heuristic output of 0.8, degraded to 0.1 if a systemic signal is active. These are explicitly baseline heuristics, NOT calibrated probabilities, serving as a placeholder until a calibrated ML model is integrated. It returns a strictly validated `RiskAssessment` object containing the `Probability` and expected value.

## 5. Cause Analysis
Cause analysis checks for an injected `LLMGateway` (abstract boundary in `gateway.py`). If the gateway fails, or is missing, `_deterministic_cause_assessment()` maps the extracted features to a simple taxonomy (`CUSTOMER_SPECIFIC` or `SYSTEMIC_DEGRADATION`). The result is a `CauseAssessment` explicitly grounded to the incoming event IDs.

## 6. Intervention Generation
Similar to Cause Analysis, `LLMGateway.generate_intervention_candidates()` is called to evaluate advanced plans. In fallback mode, `_deterministic_intervention_plan()` generates a `WAIT` candidate for systemic degradation and `CREATE_PAYMENT_LINK` for customer failures. It evaluates candidates using a ranking heuristic formula: `probability * expected_recovery_value` to select the best candidate. The result is returned as a recommendation, not an authorization.

## 7. Evidence Grounding
Every deterministic assessment iterates over the `RevenueEvent` inputs to build `EvidenceReference` objects (mapping `source_id` to `event_id.value`). This proves provenance for the recommendations.

## 8. AI / Deterministic Boundary
P06 defines an abstract `LLMGateway` for AI tasks (cause synthesis, intervention generation). This establishes the AI integration boundary, with concrete providers deferred to P10. It strictly uses mathematical/rule-based heuristics for risk, eligibility, and expected value.

## 9. Structured Model Output
The `LLMGateway` abstraction enforces returning strongly-typed `CauseAssessment` and `InterventionCandidate` objects. Provider-specific JSON parsing will live strictly in P10.

## 10. Failure / Fallback Path
A `try/except` block wraps the gateway calls. If the AI component throws an error, times out, or returns `None`, the orchestrator natively catches it and falls back to `_deterministic_cause_assessment` and `_deterministic_intervention_plan` without exposing the failure to the caller or authorizing actions.

## 11. Persistence
Persistence responsibilities are strictly separated:
- **P06**: Generates and returns typed intelligence artifacts in memory.
- **Application/Orchestration layer**: Coordinates when those artifacts are persisted. (n8n orchestrates timing but is NOT the persistence owner).
- **P03**: Owns the persistence contracts and authoritative SQLite implementation.

## 12. Policy Boundary
The analyzer explicitly returns `InterventionPlan` objects containing a `selected_action_type`. It does NOT interact with `RecoveryStateMachine` or authorize the action. P07 Policy Engine will consume this plan later.

## 13. Important Files
- `recoverai/intelligence/analyzer.py`
- `recoverai/intelligence/gateway.py`
- `tests/unit/intelligence/test_analyzer.py`

## 14. Test Coverage
Extensive testing proves:
- Deterministic paths properly rank values and build plans.
- Mock LLM gateways return abstract objects cleanly.
- Gateway failures (both Cause Synthesis and Intervention Generation) seamlessly fall back to deterministic baselines.
- Evidence references are properly typed and populated.
