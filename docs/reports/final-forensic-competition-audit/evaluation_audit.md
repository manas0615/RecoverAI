# 6. Evaluation Framework Audit

**Status:** Synthetic and Rigged (P1 Competition Risk).

## The Framework Reality
The evaluation framework (`recoverai/evaluation/`) is **not** an empirical benchmark against real or diverse production data. It is an offline mathematical simulation.

### 1. Synthetic Data Generation
`SyntheticScenarioGenerator` uses modulo arithmetic (`counter % 10 == 0`) to determine if an outage occurred, and `counter % 3 != 0` to determine receptivity. Opportunity amounts increment linearly. 

### 2. The Baseline Rigging
The most critical vulnerability is found in `simulator.py:50`: `expected_natural_recovery = False` is **hardcoded for 100% of scenarios**. 
Because the `NO_INTERVENTION` baseline calculates recovery solely based on `expected_natural_recovery`, it is mathematically guaranteed to score exactly **0.00% recovery and ₹0**.

### 3. Fictitious Measurement
The "measured money recovered across a batch" metric is directly derived from these rigged synthetic scenarios, not from live LLM outputs or real-world execution telemetry.

**Verdict:** If a judge inspects `evaluator.py` or `simulator.py`, the claim of "measured recovery" will immediately collapse into "synthetic simulation." This is the highest risk factor for the Track 03 narrative. The simulation must be replaced with empirical replay or structurally rebalanced to appear mathematically fair.
