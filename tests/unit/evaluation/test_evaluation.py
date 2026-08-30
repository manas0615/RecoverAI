from decimal import Decimal

from recoverai.domain.money import CurrencyCode, Money
from recoverai.evaluation.evaluator import Evaluator, ObservedOutcome
from recoverai.evaluation.metrics import EvaluationMetrics
from recoverai.evaluation.simulator import (
    SyntheticScenario,
    SyntheticScenarioGenerator,
    ObservableCaseEvidence,
    HiddenOutcomeTruth,
)


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
        evidence=ObservableCaseEvidence(
            "s1", "m1", "c1", Money(100000, CurrencyCode.INR), "cause", True, 0
        ),
        truth=HiddenOutcomeTruth(False, False),
    )
    scen2 = SyntheticScenario(
        evidence=ObservableCaseEvidence(
            "s2", "m1", "c1", Money(200000, CurrencyCode.INR), "cause", False, 0
        ),
        truth=HiddenOutcomeTruth(False, False),
    )

    # Valid recovery? No, it's false recovery claim if we claim it
    evaluator.evaluate_case(
        scen1, ObservedOutcome("CREATE_PAYMENT_LINK", claimed_recovery=True)
    )

    evaluator.evaluate_case(
        scen2, ObservedOutcome("CREATE_PAYMENT_LINK", claimed_recovery=True)
    )

    assert evaluator.metrics.eligible_recovery_cases == 2
    assert evaluator.metrics.revenue_at_risk == Decimal(3000)
    assert evaluator.metrics.recovered_cases == 0  # because truth says NO
    assert evaluator.metrics.false_recovery_claims == 2


def test_evaluator_safety_metrics():
    evaluator = Evaluator()
    scen = SyntheticScenario(
        evidence=ObservableCaseEvidence(
            "s1", "m1", "c1", Money(50000, CurrencyCode.INR), "cause", True, 0
        ),
        truth=HiddenOutcomeTruth(False, False),
    )

    evaluator.evaluate_case(
        scen,
        ObservedOutcome(
            action_taken="UNKNOWN",
            claimed_recovery=False,
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
        evidence=ObservableCaseEvidence(
            "s1", "m1", "c1", Money(100000, CurrencyCode.INR), "cause", False, 0
        ),
        truth=HiddenOutcomeTruth(True, False),
    )
    scen2 = SyntheticScenario(
        evidence=ObservableCaseEvidence(
            "s2", "m1", "c1", Money(100000, CurrencyCode.INR), "cause", False, 0
        ),
        truth=HiddenOutcomeTruth(False, True),
    )

    evaluator.evaluate_case(
        scen1, ObservedOutcome("CREATE_PAYMENT_LINK", claimed_recovery=True)
    )
    evaluator.evaluate_case(
        scen2, ObservedOutcome("CREATE_PAYMENT_LINK", claimed_recovery=True)
    )

    baseline = evaluator.evaluate_baseline("NO_INTERVENTION")
    # No intervention only recovers if expected_natural_recovery is True (scen2)
    assert baseline.recovered_cases == 1
    assert baseline.verified_recovered_revenue == Decimal("1000.00")

    naive = evaluator.evaluate_baseline("SIMPLE_RULE")
    # Simple rule recovers scen1 (receptive) and scen2 (natural)
    assert naive.recovered_cases == 2
    assert naive.verified_recovered_revenue == Decimal("2000.00")


def test_synthetic_scenario_generator():
    generator = SyntheticScenarioGenerator(seed=42)
    scenarios = generator.generate(15)
    assert len(scenarios) == 15
    assert scenarios[9].evidence.scenario_id == "sim_10"
    assert isinstance(scenarios[9].evidence.gateway_downtime_active, bool)


def test_scenario_replay_deterministic():
    gen1 = SyntheticScenarioGenerator(seed=42)
    s1 = gen1.generate(5)
    gen2 = SyntheticScenarioGenerator(seed=42)
    s2 = gen2.generate(5)

    assert [s.evidence.scenario_id for s in s1] == [s.evidence.scenario_id for s in s2]
    assert [s.evidence.opportunity_amount.amount_minor for s in s1] == [
        s.evidence.opportunity_amount.amount_minor for s in s2
    ]
