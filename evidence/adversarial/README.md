# Adversarial & Red-Team Evidence

This directory documents the findings of the hostile offline red-team review performed by an Antigravity Gemini 3.1 Pro QA agent.

## Critical Defects Discovered & Fixed

### Finding #1: Broken Recovery-Loop Correlation
- **Vulnerability**: The Razorpay adapter was injecting a generic `"Recovery Payment for case {case_id}"` into the payment link description, while the case manager expected a specific deterministic Action ID (`#plink_xxx`).
- **Why Tests Missed It**: The unit tests explicitly mocked the Razorpay adapter's output to match the case manager's expected format.
- **The Fix**: The adapter was modified to embed the deterministic Recovery Action ID (`"Recovery Action {action.action_id.value}"`). The case manager was updated to parse this precise tag.
- **Outcome**: A failed recovery payment now flawlessly maps back to the original action, closing the loop and bounding the retry state.

### Finding #2: Amount Verification Bypass
- **Vulnerability**: The `VerificationEngine` accepted malformed webhooks lacking an `amount` block. Because `amount` was missing, it bypassed the strict currency/value checks and blindly returned `VerifiedState.SUCCESS`.
- **Why Tests Missed It**: Automated tests always provided well-formed `amount` dictionaries matching the Razorpay spec.
- **The Fix**: `_verify_payment_link` was modified to fail closed. If `amount` is missing, it now immediately returns `VerifiedState.UNKNOWN`.
- **Outcome**: Malformed or maliciously stripped webhooks can no longer artificially trigger a successful recovery state.
