# Package 14 Walkthrough

## Synthetic Evaluation Flow
1. **Scenario Generation**: SyntheticScenarioGenerator builds a deterministic batch of SyntheticScenario instances describing simulated conditions (e.g., eceptive_to_intervention=True, systemic_degradation_active=False).
2. **Outcome Evaluation**: These hidden ground-truths are passed into an offline Evaluator. Rather than executing actual HTTP calls, the Evaluator calculates counterfactual results based on a simulated intervention path.
3. **Metric Extraction**: The outcomes increment strict metrics inside EvaluationMetrics. False recoveries heavily penalize the model and trigger alerts in safety metrics.
4. **Baseline Contrast**: Finally, .evaluate_baseline() mirrors the exact batch scenarios through naive logic to produce a reliable comparison dataset.
