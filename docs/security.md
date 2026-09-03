# Security & Trust Architecture

RecoverAI is built on a zero-trust model between the AI intelligence layer and the financial execution boundary.

## Protections

- **Frontend API Key**: Basic API protection for external invocation (intended to be replaced by full auth).
- **n8n Authorization**: The human-approval escalation route requires an explicit API key/secret matching `n8n_api_key`.
- **Razorpay Webhook HMAC**: All incoming webhooks must contain a cryptographically verifiable `X-Razorpay-Signature` matching the webhook secret.
- **Provider Evidence Verification**: The `VerificationEngine` enforces exact amount and currency matches, failing closed (`UNKNOWN`) if data is missing or malformed.
- **Deterministic Policy Authority**: `PolicyEngine` is the sole authority on financial execution. It is natively evaluated before any Razorpay adapter call.
- **High-Value Threshold**: Cases exceeding a configurable monetary threshold (default ₹40,000) are deterministically routed to `ESCALATE` requiring human review.
- **Maximum Attempts**: Closed-loop retries are strictly bounded by `max_attempts_per_case`.
- **Duplicate/Idempotency Controls**: Uniqueness constraints on `(source_type, source_event_id)` prevent double-counting webhook events.
- **Execution Claim**: Database transactions use row-level locking to prevent concurrent double-execution of the same action.
- **Systemic Degradation**: High failure rates dynamically trigger systemic degradation rules, suspending aggressive automated actions.
- **EXECUTION_UNKNOWN Protection**: Actions left in an unknown state (due to network partition or process crash) are safely quarantined for verification.
- **Invalid AI Output Behavior**: Schema violations or hallucinated actions fail gracefully; the system reverts to a safe deterministic fallback.
- **No Direct AI Financial Authority**: The AI has zero capability to invoke financial endpoints or determine if a recovery succeeded.

## Known Prototype Limitations

- **Rate Limiting**: The current `RateLimiter` is a lightweight in-memory dictionary based on `request.client.host`. It does not account for proxy identity spoofing (e.g., untrusted `X-Forwarded-For` headers) and relies on the local environment for bucket tracking.
