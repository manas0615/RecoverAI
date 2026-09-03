# Failure Recovery Mechanisms

RecoverAI is designed to safely handle failures at every layer of the technology stack, ensuring that financial state is never corrupted and that runaway automation is impossible.

## 1. Provider (Razorpay) Failures

### API Timeouts
If the `RazorpayAdapter` attempts to create a payment link and the network connection drops or times out before receiving a response, the system does not know if Razorpay actually created the link.
- **Implemented Behavior:** The `RecoveryAction` state transitions to `EXECUTION_UNKNOWN`.
- **Safety Guarantee:** The system halts automated processing for this case. It is quarantined for manual reconciliation.

### Webhook Ordering
If a `payment_link.paid` webhook arrives before the `RecoveryAction` database transaction commits, the `VerificationEngine` will not find the action.
- **Implemented Behavior:** The `VerificationEngine` throws an exception, and the API returns a 500 or 400. Razorpay will automatically retry the webhook delivery later, by which time the action will exist.

## 2. Intelligence (Gemini) Failures

### Quota Exceeded (429) or Network Error
If the live Gemini API is unreachable or rate-limits the request.
- **Implemented Behavior:** The `ConcreteLLMGateway` safely traps the exception. The `RevenueIntelligenceAnalyzer` suppresses the error and returns a predefined `GEMINI_FAILED_FALLBACK` plan. The system gracefully degrades to deterministic rules.

### Malformed AI Output
If Gemini returns an invalid JSON string or hallucinated action types.
- **Implemented Behavior:** The Pydantic parser catches the schema violation and falls back to the safe deterministic plan.

## 3. Execution & Workflow Failures

### Recovery-Payment Failure
When a customer attempts to pay via a generated Payment Link but their card is declined.
- **Implemented Behavior:** Razorpay fires a `payment.failed` webhook containing the `Action ID`. The system correlates it, marks the attempt as `VERIFIED_FAILURE`, and automatically replans a new bounded attempt.

### Bounded Recovery Attempts
To prevent runaway loops where a payment continually fails.
- **Implemented Behavior:** The `PolicyEngine` enforces `max_attempts_per_case`. Once exhausted, the policy forces a `SUPPRESS` decision, halting the loop permanently.

### Database / Infrastructure Failure
If the server crashes mid-execution.
- **Implemented Behavior:** All state mutations execute inside atomic SQLite transactions. If a crash occurs before commit, the database rolls back, and the external webhook (e.g., from Razorpay) will simply be retried by the provider.
