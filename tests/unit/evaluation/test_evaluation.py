from decimal import Decimal

from recoverai.domain.money import CurrencyCode, Money
from recoverai.evaluation.evaluator import Evaluator, ObservedOutcome
from recoverai.evaluation.metrics import EvaluationMetrics
from recoverai.evaluation.simulator import SyntheticScenario, SyntheticScenarioGenerator


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
    scen1 = SyntheticScenario(
        "s1",
        "m1",
        "c1",
        Money(100000, CurrencyCode.INR),
        "cause",
        True,
        False,
        "ACTION",
        False,
    )
    scen2 = SyntheticScenario(
        "s2",
        "m1",
        "c1",
        Money(200000, CurrencyCode.INR),
        "cause",
        False,
        False,
        "ACTION",
        False,
    )

    # Valid recovery
    evaluator.evaluate_case(scen1, ObservedOutcome("ACTION", True))

    # False recovery (observed claims recovery, but scenario ground truth says customer is not receptive and no natural recovery)
    evaluator.evaluate_case(scen2, ObservedOutcome("ACTION", True))

    assert evaluator.metrics.eligible_recovery_cases == 2
    assert evaluator.metrics.revenue_at_risk == Decimal(3000)
    assert evaluator.metrics.recovered_cases == 1
    assert evaluator.metrics.verified_recovered_revenue == Decimal(1000)
    assert evaluator.metrics.false_recoveries == 1


def test_evaluator_safety_metrics():
    evaluator = Evaluator()
    scen = SyntheticScenario(
        "s1",
        "m1",
        "c1",
        Money(50000, CurrencyCode.INR),
        "cause",
        True,
        False,
        "ACTION",
        False,
    )

    evaluator.evaluate_case(
        scen,
        ObservedOutcome(
            action_taken=None,
            verified_recovered=False,
            unauthorized_execution_attempt=True,
            policy_bypass_attempt=True,
            unknown_handled=True,
            evidence_mismatch=True,
            amount_mismatch=True,
            duplicate_evidence=True,
        ),
    )

    assert evaluator.metrics.unauthorized_execution_attempts == 1
    assert evaluator.metrics.policy_bypass_attempts == 1
    assert evaluator.metrics.unknown_handling_count == 1
    assert evaluator.metrics.incorrect_evidence_matching == 1
    assert evaluator.metrics.amount_currency_mismatch == 1
    assert evaluator.metrics.duplicate_evidence_count == 1


def test_evaluator_baseline_comparison():
    evaluator = Evaluator()
    scen1 = SyntheticScenario(
        "s1",
        "m1",
        "c1",
        Money(100000, CurrencyCode.INR),
        "cause",
        True,
        False,
        "ACTION",
        False,
    )
    scen2 = SyntheticScenario(
        "s2",
        "m1",
        "c1",
        Money(100000, CurrencyCode.INR),
        "cause",
        False,
        False,
        "ACTION",
        True,
    )

    evaluator.evaluate_case(scen1, ObservedOutcome("ACTION", True))
    evaluator.evaluate_case(scen2, ObservedOutcome("ACTION", True))

    baseline = evaluator.evaluate_baseline("NO_INTERVENTION")
    # No intervention only recovers if expected_natural_recovery is True (scen2)
    assert baseline.recovered_cases == 1
    assert baseline.verified_recovered_revenue == Decimal("1000.00")

    naive = evaluator.evaluate_baseline("NAIVE")
    # Naive recovers scen1 (receptive) and scen2 (natural)
    assert naive.recovered_cases == 2
    assert naive.verified_recovered_revenue == Decimal("2000.00")


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
