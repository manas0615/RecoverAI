# Package 09: Testing and Verification

## 1. Test Suite Evidence
The full unit test suite executes all edge-case verifications for P09 securely in an isolated, transactional in-memory database using the `pytest` fixture system. 

```bash
tests/unit/verification/test_engine.py ...........
```

### Coverage (11 Tests)
- **`test_execution_unknown_no_events_remains_unknown`**: Proves that without verifiable webhook evidence, an `EXECUTION_UNKNOWN` action does not magically resolve itself. It remains securely in a pending state until escalation.
- **`test_verified_failure_when_provider_rejects_synchronously`**: Validates the translation of a synchronous provider error (`failure_reason` presence) directly to `VERIFIED_FAILURE`.
- **`test_verified_success_when_payment_link_paid`**: Happy path. Matches `external_reference` (`plink_xxx`), asserting complete state transition `VERIFIED_SUCCESS` and `CaseWorkflowState.CLOSED`.
- **`test_verified_success_from_execution_unknown`**: Validates the P09 requirement to parse and match the `idempotency_key` internally if the execution timed out prior to learning the `external_reference`.
- **`test_amount_mismatch_fails_safely`**: Validates that if a customer pays 500 minor units but the case dictates 1000 minor units, P09 returns `VerifiedState.UNKNOWN` and fails closed safely.
- **`test_currency_mismatch_fails_safely`**: Ensures currency type mismatches fail safely.
- **`test_duplicate_evidence_handled_deterministically`**: Ensures duplicate webhooks process idempotently.
- **`test_conflicting_evidence_success_overrides_failure`**: Conflicting webhooks yield to explicitly defined positive resolution.
- **`test_terminal_case_behavior`**: Reconciler safely skips attempting to verify closed or terminal cases.

## 2. Evidence-Based Design
- `VerificationRecordRepository` explicitly tracks `checked_at` and stores an `EvidenceReference` linking directly to the underlying `RevenueEventId`. This maintains the audit history required for P13 (Audit & Observability).
