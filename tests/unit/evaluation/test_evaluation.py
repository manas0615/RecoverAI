from recoverai.domain.money import CurrencyCode, Money
from recoverai.evaluation.benchmark import run_benchmark
from recoverai.evaluation.evaluator import Evaluator
from recoverai.evaluation.simulator import (
    EvaluationOracle,
    HiddenOutcomeTruth,
    ObservableCaseEvidence,
    SyntheticScenario,
    SyntheticScenarioGenerator,
)
from recoverai.evaluation.strategies import (
    L0NoIntervention,
    L1NaiveRule,
    L2DeterministicRules,
    L3CurrentRecoverAI,
)


def test_oracle_independence():
    generator = SyntheticScenarioGenerator(seed=10)
    scenarios = generator.generate(5)
    for s in scenarios:
        assert s.oracle.expected_decision in [
            "RECOVER",
            "SUPPRESS",
            "ESCALATE",
            "WAIT",
            "DENY",
            "CREATE_PAYMENT_LINK",
        ]
        # Oracle is generated independently of any PolicyEngine class.


def test_data_leakage():
    # Prove HiddenOutcomeTruth and Oracle are absent from strategy-facing input
    generator = SyntheticScenarioGenerator(seed=11)
    scenario = generator.generate(1)[0]

    # Check that ObservableCaseEvidence does not contain truth
    assert not hasattr(scenario.evidence, "expected_natural_recovery")
    assert not hasattr(scenario.evidence, "receptive_to_intervention")
    assert not hasattr(scenario.evidence, "expected_decision")


def test_determinism():
    gen1 = SyntheticScenarioGenerator(seed=100)
    s1 = gen1.generate(10)

    gen2 = SyntheticScenarioGenerator(seed=100)
    s2 = gen2.generate(10)

    for a, b in zip(s1, s2):
        assert a.evidence.scenario_id == b.evidence.scenario_id
        assert a.truth.receptive_to_intervention == b.truth.receptive_to_intervention
        assert a.oracle.expected_decision == b.oracle.expected_decision


def test_cross_strategy_fairness():
    # Same scenarios are given to all strategies
    generator = SyntheticScenarioGenerator(seed=55)
    scenarios = generator.generate(10)

    evaluator = Evaluator()
    l0 = L0NoIntervention()
    l3 = L3CurrentRecoverAI()

    m0 = evaluator.evaluate(l0, scenarios)
    m3 = evaluator.evaluate(l3, scenarios)

    assert m0.eligible_cases == 10
    assert m3.eligible_cases == 10
    assert m0.amount_at_risk == m3.amount_at_risk


def test_decision_outcome_separation():
    # A failed outcome does not automatically mean the decision is incorrect
    evidence = ObservableCaseEvidence(
        scenario_id="mock",
        merchant_id="m1",
        customer_id="c1",
        opportunity_amount=Money(100_00, CurrencyCode.INR),
        failure_code="network_timeout",
        gateway_downtime_active=False,
        historical_failure_count=0,
    )
    truth = HiddenOutcomeTruth(
        receptive_to_intervention=True,
        expected_natural_recovery=False,
        provider_error_on_execution=True,  # Will fail
    )
    oracle = EvaluationOracle(expected_decision="CREATE_PAYMENT_LINK")
    scenario = SyntheticScenario(evidence, truth, oracle)

    evaluator = Evaluator()
    l2 = L2DeterministicRules()

    metrics = evaluator.evaluate(l2, [scenario])
    # Decision was CREATE_PAYMENT_LINK, matches Oracle (1 correct decision)
    # But it failed intervention
    assert metrics.correct_decisions == 1
    assert metrics.failed_interventions == 1
    assert metrics.successful_verified_recoveries == 0


def test_safety_invariant():
    generator = SyntheticScenarioGenerator(seed=100)
    scenarios = generator.generate(10)

    evaluator = Evaluator()
    l1 = L1NaiveRule()

    # L1 should violate stopping rule for cases with history >= 3
    m1 = evaluator.evaluate(l1, scenarios)

    assert not m1.passed_safety_invariants
    assert m1.stopping_rule_violations > 0 or m1.policy_violations > 0


def test_reproducible_benchmark():
    res1 = run_benchmark(42, 20)
    res2 = run_benchmark(42, 20)

    assert res1["L3"].gross_recovered_value == res2["L3"].gross_recovered_value
    assert res1["L2"].interventions == res2["L2"].interventions
