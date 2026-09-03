from collections import defaultdict

from recoverai.evaluation.evaluator import Evaluator
from recoverai.evaluation.simulator import SyntheticScenarioGenerator
from recoverai.evaluation.strategies import (
    L2DeterministicRules,
    L3ControlledAIRecoverAI,
    L3CurrentRecoverAI,
)


def run_attribution_benchmark(seed: int, scenarios_count: int):
    generator = SyntheticScenarioGenerator(seed=seed)
    scenarios = generator.generate(scenarios_count)

    evaluator = Evaluator()
    l2 = L2DeterministicRules()
    l3f = L3CurrentRecoverAI()
    l3a = L3ControlledAIRecoverAI()

    m2 = evaluator.evaluate(l2, scenarios)
    m3f = evaluator.evaluate(l3f, scenarios)
    m3a = evaluator.evaluate(l3a, scenarios)

    categories: dict[str, int] = defaultdict(int)

    for scenario in scenarios:
        d2 = l2.evaluate(scenario.evidence)
        d3a = l3a.evaluate(scenario.evidence)

        ai_proposed = d3a.proposed_action
        final_action = d3a.action_taken
        l2_action = d2.action_taken
        oracle_decision = scenario.oracle.expected_decision

        if ai_proposed == l2_action:
            categories["A_AGREES_WITH_L2"] += 1
        else:
            if final_action != ai_proposed:
                categories["B_DIFFERS_POLICY_OVERRIDES"] += 1
            else:
                categories["C_DIFFERS_POLICY_ALLOWS"] += 1

                if final_action == oracle_decision and l2_action != oracle_decision:
                    categories["D_DIFFERS_OUTCOME_IMPROVES"] += 1
                elif final_action != oracle_decision and l2_action == oracle_decision:
                    categories["E_DIFFERS_OUTCOME_WORSENS"] += 1
                else:
                    categories["F_DIFFERENCE_INCONCLUSIVE"] += 1

    return m2, m3f, m3a, categories


if __name__ == "__main__":
    m2, m3f, m3a, cats = run_attribution_benchmark(42, 200)
    print("--- L2 ---")
    print(
        f"Gross Recovery: {m2.gross_recovered_value} | Policy Viol: {m2.policy_violations} | Oracle Agrmnt: {m2.decision_quality_rate * 100:.1f}%"
    )
    print("--- L3-F ---")
    print(
        f"Gross Recovery: {m3f.gross_recovered_value} | Policy Viol: {m3f.policy_violations} | Oracle Agrmnt: {m3f.decision_quality_rate * 100:.1f}%"
    )
    print("--- L3-A ---")
    print(
        f"Gross Recovery: {m3a.gross_recovered_value} | Policy Viol: {m3a.policy_violations} | Oracle Agrmnt: {m3a.decision_quality_rate * 100:.1f}%"
    )
    print("\n--- AI ATTRIBUTION ---")
    for k in sorted(cats.keys()):
        print(f"{k}: {cats[k]}")
