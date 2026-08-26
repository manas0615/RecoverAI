# Package 04 — Event Ingestion Walkthrough

## 1. Webhook Entry Boundary
Ingestion is orchestrated via `recoverai.ingestion.razorpay.service.WebhookIngestionService`. It exposes a single entry function `process_webhook()` requiring raw webhook bytes, the received signature, and the external provider ID for deduplication. 

## 2. Raw Body Handling
`process_webhook` intercepts raw bytes and delegates immediately to the `WebhookVerifier`. JSON parsing is strictly blocked until verification clears.

## 3. Signature Verification
`recoverai.ingestion.razorpay.signature.WebhookVerifier` computes `hmac.new` over the raw bytes utilizing the configured `webhook_secret`. We leverage `hmac.compare_digest` to sidestep timing attacks. 

## 4. Envelope Parsing
Upon verification, the raw bytes are `json.loads` parsed. The envelope is scanned for the root `"event"` string and `"contains"` array explicitly via `RazorpayNormalizer`.

## 5. Event Dispatch
The `event` key is matched against `EVENT_TYPE_MAPPING`. If matched (e.g. `payment.failed`), execution proceeds. Unrecognized keys throw `UnsupportedWebhookEvent` (failing safely). 

## 6. Razorpay Payload Normalization
`RazorpayNormalizer.normalize()` isolates the nested `entity` block, extracting `id`, `amount`, `currency`, `customer_id`, and `created_at`. All conversions to minor integer representations happen synchronously here.

## 7. RevenueEvent Construction
The entity constructs a pure internal `RevenueEvent`. `source_event_id` is populated via the incoming header (avoiding reliance on identical nested payload IDs). 

## 8. Deduplication
Deduplication is deferred to the P03 database. If `RevenueEventRepository.save()` triggers a SQL `UNIQUE` constraint, P03 emits a `DuplicateEntityError`. 

## 9. Persistence Transaction
The save operation wraps in a `tm.transaction()` context manager. `WebhookIngestionService` catches `DuplicateEntityError` and morphs it into a `DuplicateWebhookEvent` exception.

## 10. Acknowledgement Path
To satisfy fast external acknowledgement constraints, duplicate events are caught internally, and `process_webhook` simply raises `DuplicateWebhookEvent`. The intended downstream HTTP router will catch this and render a quick 200 OK without double-processing. 

## 11. Failure Paths
Malformed signatures abort immediately (`InvalidWebhookSignature`). Bad JSON aborts as `MalformedWebhookPayload`. No partial domain state leaks.

## 12. Out-of-Order Events
Because normalization constructs independent `RevenueEvent` historical snapshots, `payment.captured` preceding `payment.failed` succeeds without errors. Conflict resolution is preserved for the later state-machine implementation (P05).

## 13. Important Files
- `recoverai/ingestion/razorpay/signature.py` (Verifier)
- `recoverai/ingestion/razorpay/normalizer.py` (Normalizer)
- `recoverai/ingestion/razorpay/service.py` (Service Integrator)
- `tests/unit/ingestion/razorpay/test_service.py` (Integration & dedup tests)
