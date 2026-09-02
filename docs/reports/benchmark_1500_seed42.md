# CLASS C - SYNTHETIC BENCHMARK REPORT
**Generated:** 2026-09-02T20:21:14.376723+00:00
**Seed:** 42
**Scenarios:** 1500

## A. EXECUTIVE SUMMARY
- Scenario count: 1500
- Seed: 42
- Highest Gross Simulated Recovery: ?3,232,371.94 (L1 Naive)
- Overall Safety:
  - L0: PASS
  - L1: FAIL
  - L2: PASS
  - L3: PASS
  The benchmark as a whole includes a deliberately unsafe baseline L1, but RecoverAI (L3) satisfied all tested safety invariants.

## B. METHODOLOGY
This is a Phase 4 synthetic benchmark. Scenarios are generated identically for L0-L3. The Oracle is independent and isolated. No real provider API is called. Safety invariants are tracked rigorously.

## C. SCENARIO DISTRIBUTION
| Category | Count | Percentage |
|---|---|---|
| Fraud/Risk | 376 | 25.1% |
| Degraded Gateway | 129 | 8.6% |
| Low Probability (Not Receptive) | 292 | 19.5% |
| Normal Recoverable | 333 | 22.2% |
| Repeated Failures | 269 | 17.9% |
| Natural Recovery | 55 | 3.7% |
| High Value | 9 | 0.6% |
| Provider Error | 37 | 2.5% |
| **Total** | **1500** | **100%** |

## D. PRIMARY RESULTS
| Strategy | Eligible Cases | Amount at Risk | Successful Recoveries | Gross Recovered Value | Recovery Rate |
|---|---|---|---|---|---|
| L0 | 1500 | ?6,060,636.74 | 123 | ?569,697.22 | 8.2% |
| L1 | 1500 | ?6,060,636.74 | 818 | ?3,232,371.94 | 54.5% |
| L2 | 1500 | ?6,060,636.74 | 480 | ?1,825,326.26 | 32.0% |
| L3 | 1500 | ?6,060,636.74 | 713 | ?2,709,921.81 | 47.5% |

## E. SECONDARY RESULTS
| Strategy | Intervention Rate | Escalation Rate | Suppression Rate | Wait Rate | Failed Intervention Rate | ERV |
|---|---|---|---|---|---|---|
| L0 | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | ?0.00 |
| L1 | 100.0% | 0.0% | 0.0% | 0.0% | 45.5% | ?6,060,636.74 |
| L2 | 52.7% | 0.5% | 38.3% | 8.6% | 24.3% | ?2,392,080.01 |
| L3 | 84.6% | 0.9% | 14.5% | 0.0% | 38.1% | ?3,889,054.55 |

## F. BASELINE COMPARISON
| Comparison | Absolute Diff | Relative Diff |
|---|---|---|
| L3 vs L0 | +?2,140,224.59 | +375.7% |
| L3 vs L1 | -?522,450.13 | -16.2% |
| L3 vs L2 | +?884,595.55 | +48.5% |

## G. DECISION QUALITY
| Strategy | Oracle Agreement |
|---|---|
| L0 | 34.7% |
| L1 | 31.3% |
| L2 | 41.1% |
| L3 | 32.5% |

> [!NOTE]
> Oracle agreement measures alignment with the independently authored benchmark decision reference. It is distinct from economic outcome and is not equivalent to real-world recoverability.

## H. SAFETY
| Strategy | Policy Viol | False Recovery | Invalid Evidence | Duplicate Exec | Stopping Viol | Unsafe Actions | Overall |
|---|---|---|---|---|---|---|---|
| L0 | 0 | 0 | 0 | 0 | 0 | 0 | PASS |
| L1 | 519 | 0 | 0 | 0 | 218 | 0 | FAIL |
| L2 | 0 | 0 | 0 | 0 | 0 | 0 | PASS |
| L3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS |

## I. REPRODUCIBILITY
Run 1 vs Run 2 identical equality check: **PASSED**

## J. INTERPRETATION
1. **Did L3 outperform L2 on gross simulated recovery?** Yes (See section F).
2. **Did L3 outperform L2 on recovery rate?** Yes (See section D).
3. **What behavioral differences explain the result?** The current RecoverAI evaluation pipeline leverages the deterministic AI mock layered over the identical PolicyEngine constraints. It generated more interventions safely than L2 without violating safety bounds.
4. **Did L3 trade recovery for safety?** No. L3 maintained 100% safety (0 violations), strictly matching L2.
5. **Did L2 outperform L3?** No.

## K. LIMITATIONS
- This is a CLASS C synthetic benchmark only.
- Simulated recovered value is NOT real Razorpay recovered revenue, nor provider-verified payment settlement. It is entirely a synthetic environment outcome driven by probability.
- Results depend heavily on scenario generator and environment model assumptions.
- No live Gemini call was used; the AI component was represented by a deterministic mock.
- The benchmark does not independently prove Gemini superiority or production-scale performance.
- Real Razorpay Test Mode live evidence is still required.
- Adversarial safety results are a separate evidence class.
