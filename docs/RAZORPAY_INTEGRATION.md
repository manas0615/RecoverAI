# Razorpay Integration

RecoverAI integrates deeply with Razorpay to execute and verify revenue recovery operations. To ensure safety, all provider integration is currently restricted to **Razorpay Test Mode**.

## Authentication & Adapter Boundary
Communication with Razorpay is handled exclusively through the `RazorpayAdapter` using Basic Auth (`RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`). The adapter acts as an anti-corruption layer, translating internal domain entities into external Razorpay payloads.

## Ingestion: payment.failed
RecoverAI listens for `payment.failed` webhooks via `/api/webhooks/razorpay`.
- **HMAC Verification:** The `X-Razorpay-Signature` is validated against the raw payload using `RAZORPAY_WEBHOOK_SECRET`.
- **Normalization:** The raw payload is mapped into a canonical `Event` object, extracting `source_event_id` (e.g., `evt_xxx`), `amount`, and `currency`.

## Execution: Payment Links
The primary recovery mechanism currently implemented is the **Payment Link** (`CREATE_PAYMENT_LINK`).
When the `RecoveryActionService` delegates execution to the adapter:
1. The adapter formats a payload for the `/v1/payment_links` endpoint.
2. It sets the amount, currency, and a default expiration.
3. **Correlation Tag:** Critically, it injects `Recovery Action {action_id}` into the `description` field.
4. Razorpay creates the link and returns a `plink_xxx` ID.
5. The adapter returns the `plink_xxx` ID as the `external_reference`.

## Verification: payment_link.paid
When the customer successfully pays the link, Razorpay fires `payment_link.paid`.
- The webhook payload contains the `plink_xxx` ID.
- The `VerificationEngine` looks up the pending `RecoveryAction` using this external reference.
- It strictly asserts that the `amount_minor` and `currency` in the webhook match the expected recovery amount.
- If verified, the case transitions to `VERIFIED_SUCCESS`.

## Closed-Loop Correlation
If the customer attempts to pay the link but the payment fails, Razorpay fires a new `payment.failed` webhook.
- The payload echoes the `description` field set during link creation.
- The `CaseManager` parses `Recovery Action {action_id}` from the description.
- This maps the failure back to the specific recovery attempt, transitioning it to `VERIFIED_FAILURE` and triggering a new replanning cycle without creating a duplicate case.
