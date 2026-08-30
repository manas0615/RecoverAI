# P25 Sensitivity Results

## Threshold Frontier
This table demonstrates the precise control RecoverAI gives a merchant over customer friction.

| Strategy (Threshold) | Recoveries | Recovered INR | Failed Interventions | Escalations |
|---|---|---|---|---|
| RecoverAI (Threshold = 2) | 701 | ₹3,002,277 | 484 | 173 |
| RecoverAI (Threshold = 3) | 727 | ₹3,159,057 | 506 | 121 |
| RecoverAI (Threshold = 4) | 760 | ₹3,244,154 | 528 | 61 |
| Simple Rule | 785 | ₹3,362,181 | 558 | 0 |

## Probability Matrix (Threshold = 3)

| Parameter | Scenario | Recoveries (Simple Rule) | Recoveries (RecoverAI) | Failed Intervs (Simple Rule) | Failed Intervs (RecoverAI) |
|---|---|---|---|---|---|
| Natural Recovery | Low (10%) | 746 | 695 | 597 | 538 |
| Natural Recovery | Baseline (15%) | 785 | 727 | 558 | 506 |
| Natural Recovery | High (20%) | 825 | 773 | 518 | 460 |
| Systemic Rate | Low (5%) | 808 | 746 | 602 | 545 |
| Systemic Rate | High (15%) | 761 | 707 | 514 | 467 |
| Receptivity | Low (50%) | 649 | 607 | 694 | 629 |
| Receptivity | High (70%) | 920 | 846 | 420 | 383 |

**Note:** All simulations used 1500 cases. 
