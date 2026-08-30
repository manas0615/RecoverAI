# P25 Result Forensic Analysis

## Phase 1 & 2: Mathematical Trace & Dependency Mapping

The evaluation traces through `SyntheticScenarioGenerator` to `Evaluator` and `RevenueIntelligenceAnalyzer` (via a deterministic fallback in `run_evaluation.py`). 

The distribution of the 1500 scenarios is generated as follows:
- 10% **Systemic Degradation**
- 20% **Repeated Failure** (maps to `true_failure_cause = "insufficient_funds"`)
- 70% Other Failure (e.g., network timeout, customer error)
- 60% **Receptive to Intervention** (independently generated)
- 5% **High Value**
- 15% **Expected Natural Recovery** (only if receptive and non-systemic)

### Strategy Logic
- **NO_INTERVENTION**: Only captures the 15% natural recovery of receptive, non-systemic cases. (112 recoveries).
- **SIMPLE_RULE**: Intervenes (`CREATE_PAYMENT_LINK`) on *all* non-systemic cases. Captures 100% of receptive cases in that bucket (799 recoveries).
- **RECOVERAI (Deterministic Fallback)**: Suppresses systemic degradation, intervenes on generic failures, **BUT escalates all `insufficient_funds` cases.** Escapated cases are NOT sent payment links, meaning they only recover if they naturally recover. (660 recoveries).

## Why RecoverAI Lost Recoveries

**The Missing 139 Recoveries:**
RecoverAI lost exactly 139 recoveries because the deterministic fallback logic explicitly hardcodes `ESCALATE` for `insufficient_funds` (Repeated Failure) cases. 
By escalating, the system avoids sending a payment link. However, the `SyntheticScenarioGenerator` independently makes 60% of these customers `receptive_to_intervention`. `SIMPLE_RULE` blindly sent them payment links and collected the money. RecoverAI escalated them and missed the money.

| Scenario Type | Simple Rule Recoveries | RecoverAI Recoveries | Difference |
|---------------|------------------------|----------------------|------------|
| Systemic      | 0 (Suppressed)         | 0 (Suppressed)       | 0          |
| Generic       | ~560                   | ~560                 | 0          |
| Insufficient Funds | ~240 (Intervened) | ~101 (Natural only)  | **-139**   |

## False Recovery Analysis

**Why did Simple Rule get 546 False Recoveries while RecoverAI got 0?**

This is an **Evaluation Model Inconsistency**.
In `evaluator.py`, `SIMPLE_RULE` increments `false_recoveries` whenever it intervenes on a customer who is *not* receptive. Thus, for `SIMPLE_RULE`, "False Recovery" actually means "Wasted/Failed Intervention on an Unreceptive Customer."

However, for `RECOVERAI`, `run_evaluation.py` passes `observed.verified_recovered = True/False` into the `evaluator.evaluate_case()` method based strictly on the ground truth receptivity. The evaluator's definition of a false recovery for the main engine is:
`is_false_recovery = observed.verified_recovered and not scenario.receptive_to_intervention`
Because the simulation script never claims `verified_recovered = True` unless the customer is receptive, RecoverAI physically cannot trigger a false recovery in the metrics.

Thus, RecoverAI looks flawlessly safe (0 false recoveries) while Simple Rule looks reckless (546 false recoveries), but in reality, RecoverAI also intervened on hundreds of unreceptive generic failure cases!

## Business Value Analysis

- **Gross Recovered INR**: SIMPLE_RULE (2.96M INR) > RECOVERAI (2.48M INR)
- **Net Merchant Value**: **The benchmark does not model net intervention cost.** There is no friction cost penalty, no SMS cost, and no customer-churn penalty for spamming unreceptive customers.

Because the simulator does not attach a financial penalty to "False Recoveries" (failed interventions), the mathematically optimal strategy in this framework is to blindly intervene on everything except systemic degradation.

## Required Judge Answers

**1. Why is Simple Rule recovering more than RecoverAI?**
Because the fallback intelligence model for RecoverAI correctly identifies `insufficient_funds` but too conservatively maps it to `ESCALATE`, dropping 139 potential recoveries that the naive Simple Rule captured via blind payment link spam.

**2. Why should a merchant choose RecoverAI anyway?**
Right now, the synthetic benchmark does not prove a monetary advantage because it does not model the financial or churn cost of spamming 546 unreceptive customers (which Simple Rule did). In a real environment, those 546 failed interventions cost SMS fees and goodwill.

**3. What does RecoverAI prevent that Simple Rule does not?**
Currently, the deterministic fallback for RecoverAI suppresses exactly the same systemic degradation as Simple Rule. The only difference is escalating insufficient funds.

**4. Are the evaluation results synthetic?**
Yes, 100% synthetic scenarios using a random number generator.

**5. What does the benchmark actually prove?**
It proves that the mathematical model works, the pipeline can process 1500 cases deterministically without breaking, and policy rules (like suppressing systemic errors) function as intended.

**6. What does the benchmark NOT prove?**
It does not prove that RecoverAI is financially superior, because the benchmark lacks an intervention cost model to penalize the naive baseline. 

**7. Does P25 measure Gemini intelligence?**
No. It exclusively measured a rule-based deterministic fallback (`AnalysisType.RULE_BASED`) written in `run_evaluation.py`.

**8. Does P25 measure policy quality?**
Yes, it successfully verified that the Policy Engine correctly handled inputs and respected suppression rules.

**9. What would need to change for RecoverAI to outperform Simple Rule?**
Two things: (1) The Evaluation Model needs to assign an explicit INR cost to failed interventions (friction cost). (2) The RecoverAI Intelligence Fallback needs to intervene on `insufficient_funds` if the customer exhibits high historical receptivity, rather than unconditionally escalating them.

## Conclusion and Final Verdict

**B & C. P25 RESULTS VALIDATED — BOTH INTELLIGENCE & EVALUATION MODELS REQUIRE IMPROVEMENT**

**Required Code Changes Identified:**
1. **Targeted Intelligence Improvement**: The deterministic fallback for RecoverAI is too simplistic. 
2. **Evaluation Model Improvement**: The definition of `false_recoveries` is inconsistent, making a direct safety comparison invalid. 

No actual code patches are generated in this phase, per rules. The result has been analyzed and documented.
