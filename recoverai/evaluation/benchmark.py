from recoverai.evaluation.simulator import SyntheticScenarioGenerator
from recoverai.evaluation.strategies import L0NoIntervention, L1NaiveRule, L2DeterministicRules, L3CurrentRecoverAI
from recoverai.evaluation.evaluator import Evaluator

def run_benchmark(seed: int, count: int) -> dict:
    generator = SyntheticScenarioGenerator(seed=seed)
    scenarios = generator.generate(count)
    
    evaluator = Evaluator()
    
    l0 = L0NoIntervention()
    l1 = L1NaiveRule()
    l2 = L2DeterministicRules()
    l3 = L3CurrentRecoverAI()
    
    metrics_l0 = evaluator.evaluate(l0, scenarios)
    metrics_l1 = evaluator.evaluate(l1, scenarios)
    metrics_l2 = evaluator.evaluate(l2, scenarios)
    metrics_l3 = evaluator.evaluate(l3, scenarios)
    
    # Calculate incremental vs L2
    metrics_l3.incremental_recovery_vs_baseline = metrics_l3.gross_recovered_value - metrics_l2.gross_recovered_value
    
    return {
        "metadata": {
            "seed": seed,
            "scenario_count": count
        },
        "L0": metrics_l0,
        "L1": metrics_l1,
        "L2": metrics_l2,
        "L3": metrics_l3
    }

if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    results = run_benchmark(seed, count)
    print(f"--- Benchmark Validation Run ---")
    print(f"Seed: {results['metadata']['seed']}, Scenarios: {results['metadata']['scenario_count']}")
    
    for level in ["L0", "L1", "L2", "L3"]:
        m = results[level]
        print(f"\n[{level}] Gross Recovery: {m.gross_recovered_value} | Interventions: {m.interventions} | False Recovery: {m.false_recovery_claims} | Policy Viol: {m.policy_violations} | Oracle Agreement: {m.decision_quality_rate * 100:.1f}%")
