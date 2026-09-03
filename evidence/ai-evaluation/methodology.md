# AI-Judgment Evaluation Methodology

This evaluation isolates Gemini's contextual reasoning capabilities from the system's deterministic execution boundaries.

## The Objective
To prove that Gemini contributes meaningful judgment when diagnosing failures and proposing interventions, beyond what simple deterministic heuristics (the baseline) can achieve. 

## The Constraints
- **Live Provider Availability:** The free tier of the live Gemini API frequently returns `429 Quota Exceeded` under sustained load.
- **Evaluation Isolation:** To cleanly separate AI reasoning quality from API availability, this evaluation uses a predefined, curated set of 10 complex scenarios. 
- **Pre-declared Expectations:** For each scenario, the preferred intervention, forbidden actions, and expected reasoning were strictly defined *before* Gemini evaluation.

## Scenario Design
The 10 scenarios represent complex failure states where naive deterministic rules often fail. They require reasoning across:
- Provider failure semantics
- Attempt history (closed-loop context)
- Systemic degradation indicators
- Customer data integrity

## Evaluation Mechanics
1. A scenario context is provided to the AI.
2. The AI generates a structured `InterventionPlan`.
3. The proposed action is compared against the pre-declared `preferred_intervention` and `forbidden_actions`.
4. The same scenario is evaluated against the `GEMINI_FAILED_FALLBACK` (deterministic baseline).
5. The results are compared to determine AI value-add.

## Trust Boundary Validation
In all cases, the AI's proposal is ultimately constrained by the `PolicyEngine`. This evaluation tracks how many *unsafe* proposals Gemini makes before policy gating, demonstrating the safety of the AI layer.
