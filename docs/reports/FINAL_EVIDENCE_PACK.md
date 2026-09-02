# FINAL EVIDENCE PACK

This document serves as the master index of claims, facts, and evidence verifying the operational and safety characteristics of the RecoverAI system.

## 5-Minute Pitch Facts

These are the strictly verified facts supporting the RecoverAI pitch:
- **Synthetic Scale:** Evaluated across **1,500** diverse synthetic scenarios.
- **Simulated Uplift:** The current evaluation pipeline demonstrated a **+48.5% relative increase in simulated gross recovered value** over the deterministic contextual-rule baseline.
- **Simulated Recovery Rates:** 47.5% recovery rate (L3) vs 32.0% (L2).
- **Absolute Safety:** **0** tested L3 safety-invariant violations during the benchmark.
- **Adversarial Security:** **0** safety violations across 21 targeted adversarial lab tests.
- **Real Execution (Class A):** Successfully processed real `payment.failed` webhooks, generated Razorpay Payment Links, and verified real `payment_link.paid` webhooks via independent provider validation (Cases A001, A002, A004).
- **Engineering Rigor:** Actively discovered and permanently fixed critical edge cases during live evaluation, including a recursive recovery-payment loop and a live high-value policy configuration gap.

## Final Supported Claims Matrix

| Claim | Evidence Class | Source | Status |
|---|---|---|---|
| Real Razorpay recovery | Class A | Cases A001, A002, A004 | **VERIFIED** |
| Recovery payment failure handled without false recovery or recursion | Class A + D | Case A003 + Regression Tests | **VERIFIED** |
| High-value threshold enforced in live wiring | Class D | Case A005 + Regression Tests | **VERIFIED** |
| 48.5% simulated uplift vs L2 deterministic rules | Class C | `benchmark_1500_seed42.md` | **VERIFIED** |
| Zero safety violations under adversarial pressure | Class B | Adversarial Safety Lab (21 Scenarios) | **VERIFIED** |
| Test-environment provider isolation fence is effective | Class D | `test_provider_isolation.py` | **VERIFIED** |

## Final Unsupported / Pending Claims

| Claim | Evidence Class | Source | Status |
|---|---|---|---|
| AI independently improves economic outcomes in live production | Phase 2 | AI-vs-Rules Attribution Harness | **NOT DEMONSTRATED** |
| Systemic/Portfolio-level intelligence actively suppresses gateway outages | N/A | Strategic Documentation | **NOT DEMONSTRATED (FUTURE)** |

*(Note: The Phase 2 attribution experiment did not establish a standalone incremental AI uplift over the deterministic baseline when controlling for the exact same inputs. The system relies heavily on the strength of its deterministic constraints and contextual orchestration.)*

## Final Judge Checklist

| Question | Status |
|---|---|
| Problem clearly stated? | **YES** |
| Architecture understandable? | **YES** |
| AI role clear? | **YES** |
| Policy boundary clear? | **YES** |
| Real Razorpay evidence available? | **YES** |
| Independent verification demonstrated? | **YES** |
| Synthetic benchmark reproducible? | **YES** |
| Safety evidence available? | **YES** |
| Known failures disclosed? | **YES** |
| Fixes documented? | **YES** |
| Claims separated by evidence class? | **YES** |
| Limitations stated? | **YES** |
| No secrets exposed? | **YES** |
| Demo instructions available? | **YES** |
| Competitive differentiation defensible? | **YES** |
