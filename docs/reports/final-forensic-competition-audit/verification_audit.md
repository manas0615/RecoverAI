# 5. Verification Forensics Audit

**Status:** Cryptographically Sound.

## P09 Verification Engine
- **Idempotency Matching:** `VerificationEngine` searches for an incoming `PAYMENT_LINK_PAID` event matching the action's `idempotency_key`.
- **Semantic Mismatch Rejection:** If the webhook amount or currency differs from the `amount_at_risk`, the system rejects the success and marks it `UNKNOWN` (preventing partial or mismatched payments from falsely clearing the ledger).
- **Audit Truth:** The `VerifiedState.SUCCESS` relies strictly on an `EvidenceReference` pointing to a securely HMAC-validated Razorpay webhook. The system cannot be tricked into marking revenue recovered without a real provider cryptographic signature.

**Verdict:** Outstanding. Verification is air-tight and evidence-based.
