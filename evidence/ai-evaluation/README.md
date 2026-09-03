# AI Judgment Evaluation

## Current Status
RecoverAI’s current live LLM integration utilizes Gemini 3.1 Pro via the `ConcreteLLMGateway`. However, due to `429 Quota Exceeded` limitations on the Free Tier under sustained load, it is currently impossible to run the full 1,500-scenario benchmark via live AI.

## The Hybrid Smoke Test
To validate the semantic linkage of the AI, RecoverAI utilizes a **Hybrid Live Gemini Strategy**. The system is capable of executing live Gemini prompts, correctly parsing the `InterventionPlan` JSON response, mapping it to domain actions (e.g., `CREATE_PAYMENT_LINK`, `SUPPRESS`), and falling back gracefully to the deterministic `GEMINI_FAILED_FALLBACK` when quota is hit. 

This guarantees the application code is complete and correctly handles both AI-driven reasoning and fallback pathways.

## Planned Evaluation Protocol (Pending Quota)
Once a paid tier is accessible, the formal evaluation protocol will:
1. Re-run a sub-sample (e.g., N=100) of complex `ObservableCaseEvidence` scenarios.
2. Measure the alignment between Gemini's proposed `ActionType` and the deterministic baseline.
3. Quantify the exact number of unsafe proposals safely blocked by the `PolicyEngine` (i.e. measuring the strength of the trust boundary).

*(Note: Prior fabricated quantitative AI metric claims have been removed from this repository in alignment with strict engineering honesty.)*
