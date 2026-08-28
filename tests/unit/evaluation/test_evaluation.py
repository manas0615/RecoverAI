from decimal import Decimal

from recoverai.evaluation.evaluator import Evaluator
from recoverai.evaluation.metrics import EvaluationMetrics
from recoverai.evaluation.simulator import SyntheticScenarioGenerator


def test_metric_correctness():
    metrics = EvaluationMetrics(
        revenue_at_risk=Decimal("1000.00"),
        verified_recovered_revenue=Decimal("500.00"),
        eligible_recovery_cases=10,
        recovered_cases=4,
    )
    assert metrics.revenue_recovery_rate == Decimal("0.5")
    assert metrics.case_recovery_rate == Decimal("0.4")


def test_metric_empty_dataset():
    metrics = EvaluationMetrics()
    assert metrics.revenue_recovery_rate == Decimal(0)
    assert metrics.case_recovery_rate == Decimal(0)


def test_evaluator_classification():
    evaluator = Evaluator()
    evaluator.add_case_result(
        amount=Decimal(1000), recovered=True, is_false_recovery=False
    )
    evaluator.add_case_result(
        amount=Decimal(2000), recovered=True, is_false_recovery=True
    )

    assert evaluator.metrics.eligible_recovery_cases == 2
    assert evaluator.metrics.revenue_at_risk == Decimal(3000)
    assert evaluator.metrics.recovered_cases == 1
    assert evaluator.metrics.verified_recovered_revenue == Decimal(1000)
    assert evaluator.metrics.false_recoveries == 1


def test_evaluator_safety_metrics():
    evaluator = Evaluator()
    evaluator.add_case_result(
        amount=Decimal(500),
        recovered=False,
        unauthorized=True,
        policy_bypass=True,
        unknown_handled=True,
        evidence_mismatch=True,
        amount_mismatch=True,
        duplicate=True,
    )
    assert evaluator.metrics.unauthorized_execution_attempts == 1
    assert evaluator.metrics.policy_bypass_attempts == 1
    assert evaluator.metrics.unknown_handling_count == 1
    assert evaluator.metrics.incorrect_evidence_matching == 1
    assert evaluator.metrics.amount_currency_mismatch == 1
    assert evaluator.metrics.duplicate_evidence_count == 1


def test_evaluator_baseline_comparison():
    evaluator = Evaluator()
    evaluator.add_case_result(Decimal(1000), True)
    evaluator.add_case_result(Decimal(1000), True)

    baseline = evaluator.evaluate_baseline("NO_INTERVENTION")
    assert baseline.recovered_cases == 0

    naive = evaluator.evaluate_baseline("NAIVE")
    assert naive.recovered_cases == 0
    assert naive.verified_recovered_revenue == Decimal("200.00")


def test_synthetic_scenario_generator():
    generator = SyntheticScenarioGenerator(seed=42)
    scenarios = generator.generate(15)
    assert len(scenarios) == 15
    assert scenarios[9].systemic_degradation_active is True
    assert scenarios[9].true_failure_cause == "system_downtime"


def test_scenario_replay_deterministic():
    gen1 = SyntheticScenarioGenerator(seed=42)
    s1 = gen1.generate(5)
    gen2 = SyntheticScenarioGenerator(seed=42)
    s2 = gen2.generate(5)

    assert [s.scenario_id for s in s1] == [s.scenario_id for s in s2]
    assert [s.opportunity_amount.amount_minor for s in s1] == [
        s.opportunity_amount.amount_minor for s in s2
    ]
