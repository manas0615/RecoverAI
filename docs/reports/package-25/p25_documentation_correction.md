# P25 Documentation Correction

## Overview
This document records the final documentation-correction pass for the P25 Synthetic Evaluation. No algorithms, models, or evaluations were rerun during this pass. 

## Issue Found
Early drafts of the P25 reporting occasionally used overly aggressive terminology (e.g., "RecoverAI wins the product race", "saving your customer relationships", "100% recall") which violated the strict evidence boundary of a synthetic benchmark. Some reports also lacked explicit disclaimers separating the synthetic evaluation of the deterministic policy from the live real-provider proof (P24) and LLM validation (P23). 

## Corrections Applied
- **Removed Overclaimed Business Value:** Replaced assumptions about customer churn and "saved relationships" with strictly measured facts ("failed interventions avoided").
- **Fixed Terminology:** Clarified that Simple Rule "aggressively maximizes intervention coverage among non-systemically degraded cases", removing the informal "100% recall" label.
- **Clarified Economic Model:** Ensured all reports explicitly state "Net merchant value is not modeled" to explain why gross recovery alone does not define a "win".
- **Separated Evidence Layers:** Explicitly reinforced that P25 did NOT measure live Gemini intelligence (which was evaluated in P23 and P24), and that P25 synthetic results are not real-world merchant revenue.
- **Consolidated Pitch/README Framing:** The README and pitch claims now strictly use the verified safety/effectiveness tradeoff text, explicitly disclosing the synthetic nature of the benchmark.

## Authoritative Numbers (Frozen)
The following numbers from the 1,500-scenario baseline benchmark (Threshold=3) are frozen and consistent across all reports:

- **Simple Rule:** 785 Recoveries, ₹3,362,181 Gross Recovery, 558 Failed Interventions
- **RecoverAI:** 727 Recoveries, ₹3,159,057 Gross Recovery, 506 Failed Interventions, 121 Escalations
- **The Delta:** RecoverAI recovered 58 fewer cases (₹203,124 less gross INR) but avoided 52 failed interventions compared to Simple Rule. 
- **False Recovery Claims:** 0 for all strategies.
- **Configurations Run:** The sensitivity analysis executed 9 benchmark configurations, each containing 1,500 scenarios, for 13,500 scenario-strategy evaluations (plus No Intervention).

## Final README-Safe Wording
> "We evaluated RecoverAI on a reproducible 1,500-scenario synthetic benchmark against no intervention and a transparent simple-rule baseline. RecoverAI did not maximize gross recovery: at the baseline configuration it recovered ₹3.16M versus ₹3.36M for the simple rule. Instead, it reduced failed interventions from 558 to 506 and escalated 121 chronic-failure cases. A predeclared sensitivity sweep showed that this recovery-versus-intervention tradeoff remained directionally stable across reasonable parameter changes. These are synthetic evaluation results, not claims of production recovery performance."

## Final Pitch-Safe Wording
> "Our synthetic 1,500-case evaluation shows an important tradeoff: a simple rule recovers more gross revenue by intervening more aggressively, while RecoverAI sacrifices some gross recovery to reduce failed interventions and escalate chronic failure patterns. The benchmark is deliberately synthetic; our real-provider proof is shown separately through Razorpay Test Mode."
