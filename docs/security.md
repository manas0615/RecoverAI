# Security & Trust Boundary Architecture

RecoverAI is engineered on a zero-trust model. The system operates under the assumption that AI outputs may be hallucinated, network providers may replay messages, and API limits may be abused.

## 1. Cryptographic Ingestion
**Webhook HMAC:** All inbound webhooks to `/api/webhooks/razorpay` are cryptographically verified by the `RazorpaySignatureValidator`. It computes an HMAC-SHA256 signature using the raw request body and the secret, comparing it against the `X-Razorpay-Signature` header. Unsigned or invalid requests are instantly rejected (HTTP 400).

## 2. Idempotency & Replay Protection
**Webhook Deduplication:** The `EventRepository` enforces a strict SQLite `UNIQUE` constraint on `(source_type, source_event_id)`. If Razorpay replays a webhook, the database natively rejects it, preventing the `CaseManager` from double-processing.

## 3. Financial Execution Barrier
**Deterministic Policy Authority:** The `PolicyEngine` is the sole authority for financial execution. Gemini's `InterventionPlan` is merely a proposal. If Gemini proposes `CREATE_PAYMENT_LINK`, the `PolicyEngine` evaluates the proposal against the case's current state.

**High-Value Threshold:** Implemented in `PolicyEngine`. Cases exceeding `high_value_threshold` (default ₹40,000) are deterministically routed to `ESCALATE` for human review via n8n. The AI cannot bypass this.

**Attempt Limits:** Implemented in `PolicyEngine`. Retries are strictly bounded by `max_attempts_per_case`.

**Atomic Execution Claim:** The `RecoveryActionService` utilizes row-level locking during the state transition from `AUTHORIZED` to `EXECUTING` to prevent a race condition where a concurrent request might double-execute an action.

## 4. Verification Integrity
**Exact Evidence Matching:** The `VerificationEngine` requires exact payloads. A payment is not "recovered" simply because a webhook arrived. The engine verifies that the `amount_minor` and `currency` in the webhook perfectly match the case's `amount_at_risk`. 

**Missing Block Defense:** If a malformed webhook arrives lacking the `amount` block entirely, the `VerificationEngine` fails closed to `EXECUTION_UNKNOWN`.

## 5. Resilience Controls
**Systemic Degradation:** (Architectural Capability) High regional failure rates can dynamically trigger systemic degradation rules in the `PolicyEngine`, suppressing aggressive automated actions to prevent overwhelming the gateway.

**EXECUTION_UNKNOWN Quarantine:** Actions left in an ambiguous state due to a Razorpay API timeout are safely transitioned to `EXECUTION_UNKNOWN`. They require explicit manual reconciliation and cannot be automatically retried.

**LLM Failure / Fallback:** If Gemini is unavailable, hits a `429 Quota Exceeded`, or returns invalid JSON schema, the `ConcreteLLMGateway` and `Analyzer` safely catch the exception and return the deterministic `GEMINI_FAILED_FALLBACK` plan.

## 6. Access Boundaries
- **Frontend vs n8n Credentials:** Internal API routes are protected by a prototype API key (`api_key` header). The n8n approval webhooks require a separate `n8n_api_key`.
- **Rate Limiting:** The `/analyze` endpoint employs a lightweight, prototype in-memory rate limiter based on `request.client.host`. *(Note: As a prototype, it does not currently account for `X-Forwarded-For` spoofing).*
- **Provider Isolation:** Razorpay execution is strictly isolated to Test Mode. Tests mock the adapter to ensure the production database is never mutated by the test harness.
- **Secret Handling:** All secrets (`RAZORPAY_KEY_SECRET`, `GEMINI_API_KEY`) reside purely server-side via environment variables and are never leaked to the React frontend.
