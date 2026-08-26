# Package 04 — Event Ingestion

## Status

IMPLEMENTED / VERIFIED

## Objective

Establish the reliable, secure, and idempotent boundary for ingesting external Razorpay webhooks. Transform them into normalized domain `RevenueEvent` instances and persist them transactionally without invoking synchronous downstream workflows or changing the pure domain models.

## Event Ingestion Architecture

A strict unidirectional pipeline:
`raw webhook bytes -> WebhookVerifier -> RazorpayNormalizer -> WebhookIngestionService -> RevenueEventRepository (P03)`

## Razorpay Documentation Verified

- Razorpay webhook validation: https://razorpay.com/docs/webhooks/validate-test/
- Razorpay payment webhooks: https://razorpay.com/docs/webhooks/payments/
- Razorpay Payment Link webhooks: https://razorpay.com/docs/webhooks/payment-links/
- Razorpay general webhook behavior: https://razorpay.com/docs/webhooks/

## Signature Verification

Implemented exactly per Razorpay documentation via `recoverai.ingestion.razorpay.signature.WebhookVerifier`.
It mandates raw bytes (preventing equivalent-JSON bypasses), uses `hmac.new` with `hashlib.sha256`, and verifies via constant-time `hmac.compare_digest`. Secrets are isolated from logs and domain models.

## Webhook Envelope Validation

Normalizer checks for dictionary structure, explicitly requires an `event` key, extracts the entity deterministically via the `contains` list, and maps core fields explicitly.

## Event ID / Deduplication

Uses the provided header `x-razorpay-event-id` (passed into `process_webhook`) as the `source_event_id`. P03's SQL `UNIQUE(source_type, source_event_id)` acts as the authoritative deduplication gate. Duplicates trigger a `DuplicateEntityError` which the `WebhookIngestionService` converts into a `DuplicateWebhookEvent` exception. The future HTTP layer is expected to catch this and safely map it to a successful duplicate 200 OK acknowledgement to satisfy Razorpay's delivery requirements without raising unhandled HTTP 500s.

## Event Normalization

`RazorpayNormalizer` acts as the mapping boundary translating the Razorpay envelope to internal `RevenueEvent` attributes. Razorpay's `amount` and `currency` are successfully transformed to internal integer-only `Money` objects. No Razorpay fields are leaked onto the `RevenueEvent` domain classes.

## Supported Event Types

Only required MVP events are parsed and dispatched:
- `payment.authorized` -> `PAYMENT_AUTHORIZED`
- `payment.captured` -> `PAYMENT_CAPTURED`
- `payment.failed` -> `PAYMENT_FAILED`
- `payment_link.paid` -> `PAYMENT_LINK_PAID`
- `payment.downtime.started` / `payment.downtime.updated` -> `PAYMENT_DEGRADATION_SIGNAL`

## Event Ordering Handling

The pipeline natively persists out-of-order events. For example, `payment.captured` arriving before `payment.failed` is perfectly permissible; each webhook creates its own independent `RevenueEvent` tracking both historical observations.

## Persistence Integration

Delegates directly to P03's `TransactionManager` and `RevenueEventRepository`. P04 constructs no SQL. 

## Error Handling

Mapped securely via domain-level errors:
- `InvalidWebhookSignature`
- `MalformedWebhookPayload`
- `UnsupportedWebhookEvent`
- `DuplicateWebhookEvent`

These exceptions do not expose secrets or sensitive payloads back to external callers.

## Security

Raw byte comparison natively protects the webhook entry. No `eval()`, `exec()`, or unstructured SQL executions exist in the pipeline.

## Observability

Standard structured `logger.info` and `logger.error` points capture `event_id`, parsing faults, duplicate identifications, and signature validation outcomes without leaking PII or full JSON.

## Files Created

- `recoverai/ingestion/exceptions.py`
- `recoverai/ingestion/razorpay/signature.py`
- `recoverai/ingestion/razorpay/normalizer.py`
- `recoverai/ingestion/razorpay/service.py`
- `tests/unit/ingestion/razorpay/test_signature.py`
- `tests/unit/ingestion/razorpay/test_normalizer.py`
- `tests/unit/ingestion/razorpay/test_service.py`

## Files Modified

None (outside of `recoverai/ingestion/` and its test modules).

## Dependencies

No new dependencies added. Built fully on Python standard library (`hmac`, `hashlib`, `json`).

## Tests

Test matrix covers:
- Valid and tampered HMAC signatures.
- Byte-equivalent vs semantic-equivalent JSON bypass attempts.
- Ingestion + Transactional Database Deduplication against P03's in-memory temp DBs.
- Malformed payloads and missing `contains` envelopes.

## Known Limitations

- Real HTTP framework (e.g., FastAPI) routing is intentionally deferred to P15.
- Test Mode secret injection is simulated in unit tests instead of leveraging live `.env` fixtures.

## Unexpected Findings

None. Architecture constraints flowed natively.

## Exact Git Commit SHAs

Implementation Commit: (See git output)
Documentation Commit: (See git output)
