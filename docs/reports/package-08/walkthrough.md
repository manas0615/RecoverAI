# P08 Walkthrough

1. A `RecoveryAction` generated as a resolution is processed.
2. The `RazorpayExecutionService` verifies the internal state boundary through P05 transition mechanics, mutating state formally via `action.begin_execution()`.
3. The underlying `RazorpayAdapter` performs authorization validation against the provided `PolicyDecision`.
4. It prepares a payload ensuring integers (`Money.amount_minor`) map correctly to Razorpay's format constraint and issues a `POST` request to the provider API using `urllib.request`.
5. Upon conclusion, execution outcomes are formally mapped:
   - Success (`2xx`): Translates via `action.record_verification` to `VERIFICATION_PENDING`.
   - Client Reject (`4xx` / pre-send failures): Handled directly as `VERIFIED_FAILURE`.
   - Transport Timeouts (`urllib` Timeout/Errors): Logged without blind retries and placed into `EXECUTION_UNKNOWN`.
6. The service updates the external reference correlation ID to match the generated Payment Link (`plink_xxx`) within P03 SQLite context.
