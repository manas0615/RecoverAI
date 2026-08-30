# P25 V2 Robustness Analysis

## Objective
To determine if RecoverAI's strategy (prioritizing precision via `historical_failure_count`) depends heavily on arbitrary assumptions or specific thresholds, and to prove whether the conclusion is credible.

## Findings
The evaluation subjected the benchmark to a 9-configuration matrix, modifying the escalation threshold, natural recovery probability, systemic degradation probability, and user receptivity.

### Sensitivity to Natural Recovery (10%, 15%, 20%)
When Natural Recovery was changed:
- **Low (10%)**: RecoverAI recovered 695 cases. Simple Rule: 746 cases.
- **High (20%)**: RecoverAI recovered 773 cases. Simple Rule: 825 cases.
- **Conclusion**: The delta remains stable. The relative tradeoff (fewer gross recoveries but fewer failed interventions) holds.

### Sensitivity to Receptivity (50%, 60%, 70%)
When Receptivity was changed:
- **Low (50%)**: RecoverAI recovered 607 cases. Simple Rule: 649 cases.
- **High (70%)**: RecoverAI recovered 846 cases. Simple Rule: 920 cases.
- **Conclusion**: Same as above. Both strategies perform better on more receptive cohorts, but the safety frontier holds.

### Sensitivity to Systemic Outages (5%, 10%, 15%)
When Systemic Failures changed:
- **Low (5%)**: RecoverAI recovered 746 cases. Simple Rule: 808 cases.
- **High (15%)**: RecoverAI recovered 707 cases. Simple Rule: 761 cases.
- **Conclusion**: Both strategies perfectly suppress systemic outages, meaning their relative relationship is unaffected by this parameter.

### Sensitivity to Escalation Threshold
We varied the `historical_failure_count` threshold required for RecoverAI to escalate instead of pinging:
- **Threshold 2**: 173 Escalations, 484 Failed Interventions, 701 Recoveries.
- **Threshold 3 (Base)**: 121 Escalations, 506 Failed Interventions, 727 Recoveries.
- **Threshold 4**: 61 Escalations, 528 Failed Interventions, 760 Recoveries.
- **Simple Rule (Infinite)**: 0 Escalations, 558 Failed Interventions, 785 Recoveries.

## Final Verdict
**ROBUST**
The safety/effectiveness tradeoff survives reasonable parameter changes. Changing probabilities shifts the absolute numbers, but not the relative ranking or the qualitative conclusion. RecoverAI's safety frontier is real and tunable.
