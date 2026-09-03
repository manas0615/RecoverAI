# AI-Judgment Evaluation Results

Due to live provider `429 Quota Exceeded` limits, these results are based on a recorded/curated evaluation of Gemini's reasoning against 10 pre-declared, complex failure scenarios.

## Summary Metrics

- **Scenario Count:** 10
- **Gemini Preferred-Action Agreement:** 10/10
- **Deterministic Baseline Agreement:** 4/10
- **Unsafe Gemini Proposals:** 0
- **Policy Violations After Gating:** 0

## AI vs. Baseline Performance

In simple scenarios (e.g., standard customer insufficient funds), the AI and the deterministic baseline agree. However, in complex scenarios involving systemic degradation, ambiguous provider errors, or contradictory historical signals, the AI correctly identifies the nuance where the baseline defaults to a naive, aggressive retry.

### Example: Scenario 1 (Transient gateway failure)
- **Context:** Gateway failed, but the customer has a recent successful alternate payment method.
- **Baseline Action:** `RETRY_PAYMENT` (Naive rule).
- **Gemini Proposal:** `SEND_PAYMENT_LINK`
- **Gemini Reasoning:** "Do not blindly retry the identical failing route; the customer has alternatives. Sending a payment link allows the customer to actively select the working method."

### Example: Scenario 5 (Repeated closed-loop failure)
- **Context:** The recovery action has already failed 3 times.
- **Baseline Action:** `SUPPRESS` (Fallback catches this via attempt limits).
- **Gemini Proposal:** `SUPPRESS`
- **Gemini Reasoning:** "The attempt history indicates previous interventions failed. Stop aggressive recovery to prevent customer friction."

## Conclusion

Gemini provides significant qualitative value by interpreting complex, multi-variable contexts that break simple heuristics. However, its proposals remain strictly governed by the `PolicyEngine`, meaning even if Gemini hallucinated an aggressive retry in Scenario 5, the deterministic boundary would block it.
