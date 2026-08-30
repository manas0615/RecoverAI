# P25 Benchmark Methodology (V2)

## 1. Information Boundary Enforcement
The evaluation framework mathematically guarantees that the **Recovery Engine (RecoverAI or Baseline)** cannot access hidden outcome truths during decision making.

### Observable Evidence (Available to Engine)
- `opportunity_amount` (INR minor units)
- `failure_code` (e.g. `insufficient_funds`, `system_downtime`)
- `gateway_downtime_active` (boolean)
- `historical_failure_count` (int)

### Hidden Outcome Truth (Used ONLY by Simulator)
- `receptive_to_intervention` (boolean)
- `expected_natural_recovery` (boolean)

## 2. Fairness Matrix
All strategies were evaluated against identical scenarios using identical evidence.

| Property | NO_INTERVENTION | SIMPLE_RULE | RECOVERAI |
|---|---|---|---|
| Same Observable Evidence | Yes | Yes | Yes |
| Same Scenarios Evaluated | Yes (1500) | Yes (1500) | Yes (1500) |
| Same Hidden Outcomes | Yes | Yes | Yes |
| Same Outcome Simulator | Yes | Yes | Yes |

## 3. Metric Definitions
To prevent the evaluation model from unfairly masking unsafe behavior, the following definitions are applied globally:
- **Failed Intervention:** The strategy chose to intervene (`CREATE_PAYMENT_LINK`), but the customer was unreceptive.
- **False Recovery Claim:** The strategy claimed a recovery in its execution trace, but the Outcome Simulator determined it was impossible based on ground truth. (This was corrected in V2 to apply consistently).
- **Unknown Handling:** The strategy threw an error or generated an unparseable action.

## 4. Economic Costs
**Net merchant value is not modeled.**
The benchmark tracks total revenue at risk, verified recovered revenue, and attempted interventions. However, no explicit INR deduction is made for a failed intervention (friction/SMS cost). Therefore, the evaluation strictly reports gross performance and safety constraints.
