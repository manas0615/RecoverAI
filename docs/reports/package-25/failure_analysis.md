# P25 Failure Analysis (V2)

## Clarification of "Failed Interventions"
In V1 of the benchmark, the evaluator incorrectly merged the concept of a "Failed Intervention" with a "False Recovery Claim". V2 explicitly separates them.

### False Recovery Claims = 0
Across 13,500 total evaluation runs in the sensitivity matrix, the RecoverAI policy engine NEVER claimed a recovery that did not occur. The safety mechanisms correctly prevented any hallucination or false logging.

### Failed Interventions
A failed intervention occurs when the system legitimately decides to attempt a recovery (`CREATE_PAYMENT_LINK`), but the customer is unreceptive (e.g., they just ignore the link). 

In the Baseline (Threshold=3) scenario:
- **Simple Rule**: 558 Failed Interventions
- **RecoverAI**: 506 Failed Interventions

RecoverAI "failed" less often because it correctly identified chronically failing customers and escalated them instead.

## Where RecoverAI "Failed" to Recover Revenue
RecoverAI surrendered 58 recoveries compared to the naive Simple Rule.
This happened entirely within the `insufficient_funds` with `historical_failure_count > 3` cohort. In the synthetic ground truth, a small percentage of customers who have failed 4 times will actually succeed if you ping them a 5th time. 

RecoverAI made the strategic policy decision that pinging a customer for a 5th time is inherently unsafe and recognizes customer friction is a motivating product concern. It deliberately "failed" to capture those 58 recoveries in order to guarantee brand safety.
