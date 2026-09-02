# REAL RAZORPAY EVIDENCE (CLASS A)

This document captures the verified, real-world execution of the RecoverAI system against the live Razorpay Test Mode API. It serves as Class A evidence of system end-to-end viability.

## What It Proves
- Real provider API connectivity and authentication.
- Real parsing of `payment.failed` webhook events into recovery cases.
- Real Payment Link creation via the Razorpay API.
- Live simulated customer payments in the Test Mode environment.
- Real ingestion and processing of `payment_link.paid` events.
- Independent verification and correlation of provider evidence before asserting success.

## Live Cases Executed

| Case | Amount | Initial Event | Action | Provider Outcome | Verification | Final Result | Key Finding |
|---|---|---|---|---|---|---|---|
| A001 | ₹100 | `payment.failed` | `CREATE_PAYMENT_LINK` | `payment_link.paid` | Verified | **VERIFIED RECOVERY** | Initial E2E success. |
| A002 | ₹450 | `payment.failed` | `CREATE_PAYMENT_LINK` | `payment_link.paid` | Verified | **VERIFIED RECOVERY** | Repeated E2E success. |
| A003 | ₹750 | `payment.failed` | `CREATE_PAYMENT_LINK` | `payment.failed` | None | **FAILED RECOVERY** | Discovered the recovery-payment failure loop. A failed recovery link generated a new `payment.failed` event, causing the system to mistakenly create a secondary recovery case. Fixed and regression-tested. |
| A004 | ₹1,000 | `payment.failed` | `CREATE_PAYMENT_LINK` | `payment_link.paid` | Verified | **VERIFIED RECOVERY** | Proved that the system remains capable of full recovery after implementing exact correlation logic to fix the A003 loop. |
| A005 | ₹50,000 | `payment.failed` | `CREATE_PAYMENT_LINK` | NOT CAPTURED | None | **ESCALATED** | Discovered a live configuration gap. The system correctly simulated a ₹40,000 threshold in the Phase 4 benchmark, but the live endpoints omitted the threshold injection. We fixed the configuration pipeline, rendering the system safe for high-value cases. A005 itself acts as preserved evidence of the flaw, not a successful recovery. |

## Important Notice
- Real money was **not** moved. All actions occurred strictly within Razorpay's Test Mode environment.
- The numbers presented here are not statistically significant for measuring overall performance; they represent integration and lifecycle viability. For population-level performance measurements, refer to the Class C Synthetic Benchmark.
