# Package 09: Verification Walkthrough

## 1. Scenario: Synchronous Failure
- **Trigger:** P08 attempts to create a Razorpay link but fails (e.g., HTTP 400).
- **P08 Boundary:** Action becomes `VERIFICATION_PENDING` with `failure_reason` set.
- **P09 Reconciler:** Observes missing `external_reference` but present `failure_reason`. 
- **Result:** Generates a `VerificationRecord` of `VerifiedState.FAILURE`. Action becomes `VERIFIED_FAILURE`. Case advances to `PLANNING` for another attempt if eligible.

## 2. Scenario: Payment Paid Successfully
- **Trigger:** P08 creates the link successfully (HTTP 200). `external_reference` is populated (`plink_xxx`).
- **P04 Boundary:** Customer pays. `PAYMENT_LINK_PAID` webhook arrives and is normalized to a `RevenueEvent`.
- **P09 Reconciler:** Finds the event matching `external_reference`, verifies `CurrencyCode` and integer `amount_minor` exactly match the `amount_at_risk`.
- **Result:** Generates `VerifiedState.SUCCESS`. Action transitions to `VERIFIED_SUCCESS`. Case `workflow_state` moves to `CLOSED` and `outcome_type` is `RECOVERED`.

## 3. Scenario: The 'Timeout' Dilemma
- **Trigger:** P08 encounters an HTTP timeout. Action goes to `EXECUTION_UNKNOWN`.
- **State:** No `external_reference` is available.
- **P09 Reconciler:** Uses the known `idempotency_key` (truncated hash of `action_id`). It queries normalized events for the merchant. It uses the integration boundary (`RazorpayEventParser`) to inspect nested webhook metadata.
- **Result:** If it finds the webhook containing the `reference_id`, it considers the action `VERIFIED_SUCCESS` despite the initial timeout, sealing the case safely.

## 4. Scenario: Amount Mismatch
- **Trigger:** Customer uses a manipulated client or partial payment is recorded, mismatching the `amount_at_risk` exactly.
- **P09 Reconciler:** Discovers a `PAYMENT_LINK_PAID` event, but the `amount_minor` differs.
- **Result:** Returns `VerifiedState.UNKNOWN`, retaining the `VERIFICATION_PENDING` state and averting an unsafe closure. This correctly queues it for escalation / bounded timeout.
