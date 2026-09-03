# Adversarial & Red-Team Validation

This directory documents the results of an offline, hostile QA audit performed against the RecoverAI repository to validate the integrity of its trust boundaries.

## Test Scope

The red-team validation focused exclusively on testing the resilience of the deterministic constraints:
- API payload manipulation
- Provider webhook spoofing
- Race conditions / concurrency
- AI hallucination handling

## Critical Engineering Findings

The audit discovered two genuine structural defects in the prototype implementation. They have been permanently fixed and are now enforced via regression testing.

### 1. Broken Recovery-Loop Correlation
- **Threat Vector**: If the closed-loop tracking breaks, the system will sprout infinite retries because the `PolicyEngine` cannot track attempt history properly.
- **Defect Found**: The Razorpay adapter was injecting a generic `"Recovery Payment for case {case_id}"` into the payment link description, instead of the strict `RecoveryActionId`. The parser could not correlate subsequent failures.
- **Fix Applied**: The `RazorpayAdapter` now strictly injects `"Recovery Action {action_id}"`. The `CaseManager` correctly parses this deterministic tag to map failures back to the originating action.
- **Regression Status**: `test_recovery_loop.py` enforces this correlation mechanism.

### 2. Missing Amount Verification Bypass
- **Threat Vector**: A malformed webhook could spoof a successful recovery by omitting the `amount` metadata, bypassing the strict value-matching logic.
- **Defect Found**: The `VerificationEngine` lacked a null-check for the `amount` dictionary in incoming payloads. When missing, the check was skipped, defaulting to `VERIFIED_SUCCESS`.
- **Fix Applied**: `_verify_payment_link` now fails closed. If `amount` or `currency` is missing from the payload, it strictly returns `VERIFIED_UNKNOWN`.
- **Regression Status**: `test_engine.py` enforces closed-failure for malformed evidence.

## Validated Protections

The audit also verified that the following protections function flawlessly:
- **Duplicate Webhook Delivery**: Blocked natively via SQLite `UNIQUE` constraints on `source_event_id`.
- **Concurrent Double-Execution**: Blocked via atomic row-level locking on the `RecoveryAction` table.
- **High-Value Policy Bypass**: Blocked by the `PolicyEngine` refusing to authorize automated actions above threshold.
- **Malformed AI Output**: Handled gracefully. Pydantic parser catches invalid JSON schemas and falls back to deterministic rules.
