# PRE-P25 FINAL RE-AUDIT — VERIFICATION RE-AUDIT

---

## 1. Evidence-Based Verification

- **Evidence Requirement:** Reconciliation requires a matching `PAYMENT_LINK_PAID` event mapped via `external_reference` or `idempotency_key`.
- **Value Verification:** Validates amount and currency against case records. Mismatches return `VerifiedState.UNKNOWN` instead of closing the case.

---

## 2. Audit Evidence Ledger

- **Verification Audit Event:** Emits `AuditEventType.VERIFICATION_COMPLETED` during production reconciliation flows.
- **Workflow State Consistency:** Case state transitions to `CLOSED` / `RECOVERED` in perfect sync with the audit record.
