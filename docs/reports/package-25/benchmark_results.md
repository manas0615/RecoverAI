# P25 Benchmark Results (V2)

**Sample Size:** 1500 Scenarios
**Total Revenue at Risk:** 6,178,033.91 INR

| Metric | No Intervention | Simple Rule | RecoverAI |
|---|---|---|---|
| **Recoveries (Cases)** | 131 | 785 | 727 |
| **Recovery Rate (Case)** | 8.7% | 52.3% | 48.5% |
| **Recovered INR** | ₹510,594 | ₹3,362,181 | ₹3,159,057 |
| **Intervention Attempts** | 0 | 1343 | 1222 |
| **Failed Interventions** | 0 | 558 | 506 |
| **False Recovery Claims** | 0 | 0 | 0 |
| **Escalations** | 0 | 0 | 121 |
| **Suppressions** | 1500 | 157 | 157 |
| **UNKNOWN Handling** | 0 | 0 | 0 |
| **Safety Violations** | 0 | 0 | 0 |

## Analysis
The result clearly shows the trade-off implemented in the RecoverAI Deterministic Fallback V2:
- RecoverAI explicitly **Escalated 121 cases** (specifically `insufficient_funds` cases where the `historical_failure_count > 3`). 
- Simple Rule indiscriminately pinged those cases.
- As a result, RecoverAI successfully avoided **52 Failed Interventions** on chronically unreceptive customers (Simple Rule 558 vs RecoverAI 506).
- However, RecoverAI also surrendered **58 Recoveries** because some of those chronic failures were, in fact, receptive to a payment link.
