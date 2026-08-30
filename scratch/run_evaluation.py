import asyncio
import json
import os
from datetime import datetime, timezone

from recoverai.evaluation.simulator import SyntheticScenarioGenerator
from recoverai.evaluation.evaluator import Evaluator, ObservedOutcome
from recoverai.policy.engine import PolicyEngine, PolicyContext
from recoverai.domain.assessment import CauseAssessment, CauseCategory, AnalysisType
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus, RevenueSource
from recoverai.domain.money import RevenueAmount
from recoverai.domain.plan import (
    InterventionPlan,
    InterventionCandidate,
    CandidateStatus,
)
from recoverai.domain.action import ActionType
from recoverai.domain.evidence import Probability
from recoverai.domain.identifiers import (
    RecoveryCaseId,
    MerchantId,
    CustomerId,
    RevenueEventId,
)


def run_one_evaluation(
    prob_systemic=0.10,
    prob_receptive=0.60,
    prob_natural_recovery=0.15,
    threshold=3,
    sample_size=1500,
    seed=123,
):
    generator = SyntheticScenarioGenerator(
        seed=seed,
        prob_systemic=prob_systemic,
        prob_receptive=prob_receptive,
        prob_natural_recovery=prob_natural_recovery,
    )
    scenarios = generator.generate(sample_size)

    evaluator = Evaluator()

    def generate_id():
        return "test_id"

    policy_engine = PolicyEngine(generate_decision_id=generate_id)

    for scenario in scenarios:
        evidence = scenario.evidence

        case = RecoveryCase(
            case_id=RecoveryCaseId(evidence.scenario_id),
            merchant_id=MerchantId(evidence.merchant_id),
            customer_id=CustomerId(evidence.customer_id),
            amount_at_risk=RevenueAmount(money=evidence.opportunity_amount),
            revenue_source=RevenueSource.SUBSCRIPTION,
            status=RecoveryCaseStatus.OPEN,
            opened_at=datetime.now(timezone.utc),
            source_event_ids=[RevenueEventId("evt_1")],
        )

        if evidence.gateway_downtime_active:
            cat = CauseCategory.SYSTEMIC_DEGRADATION
            proposed_action = ActionType.SUPPRESS
        elif evidence.failure_code == "insufficient_funds":
            cat = CauseCategory.INSUFFICIENT_FUNDS
            if evidence.historical_failure_count > threshold:
                proposed_action = ActionType.ESCALATE
            else:
                proposed_action = ActionType.CREATE_PAYMENT_LINK
        else:
            cat = CauseCategory.TECHNICAL_ERROR
            proposed_action = ActionType.CREATE_PAYMENT_LINK

        cause_assessment = CauseAssessment(
            cause_assessment_id="cause_1",
            case_id=case.case_id,
            category=cat.value,
            confidence=Probability(value=0.8, meaning="high"),
            analysis_type=AnalysisType.RULE_BASED,
            model_version="2.0",
            created_at=datetime.now(timezone.utc),
        )

        plan = InterventionPlan(
            plan_id="plan_1",
            case_id=case.case_id,
            candidates=[
                InterventionCandidate(
                    candidate_id="cand_1",
                    case_id=case.case_id,
                    action_type=proposed_action,
                    expected_recovery_probability=Probability(
                        value=0.9, meaning="high"
                    ),
                    expected_recovery_value=RevenueAmount(
                        money=evidence.opportunity_amount
                    ),
                    eligibility_status=CandidateStatus.PROPOSED,
                )
            ],
            selected_action_type=proposed_action,
            selection_reason="Deterministic fallback v2",
            selection_model_version="2.0",
            created_at=datetime.now(timezone.utc),
            expected_recovery_value=RevenueAmount(money=evidence.opportunity_amount),
        )

        context = PolicyContext(
            policy_version="1.0", current_time=datetime.now(timezone.utc)
        )

        policy_decision = policy_engine.evaluate(
            context=context,
            case=case,
            plan=plan,
            action_history=[],
            cause=cause_assessment,
        )

        if policy_decision.decision.value == "APPROVE":
            action_taken = proposed_action.value
        elif policy_decision.decision.value == "ESCALATE":
            action_taken = "ESCALATE"
        elif policy_decision.decision.value == "SUPPRESS":
            action_taken = "SUPPRESS"
        else:
            action_taken = "UNKNOWN"

        outcome = ObservedOutcome(
            action_taken=action_taken,
            unauthorized_execution_attempt=False,
            policy_bypass_attempt=False,
            unknown_handled=(action_taken == "UNKNOWN"),
            evidence_mismatch=False,
            amount_mismatch=False,
            duplicate_evidence=False,
            claimed_recovery=False,
        )

        evaluator.evaluate_case(scenario, outcome)

    base_ni = evaluator.evaluate_baseline("NO_INTERVENTION")
    base_sr = evaluator.evaluate_baseline("SIMPLE_RULE")
    recoverai_metrics = evaluator.metrics

    return {
        "metadata": {
            "evaluation_mode": "DETERMINISTIC FALLBACK V2",
            "sample_size": len(scenarios),
            "seed": seed,
            "params": {
                "prob_systemic": prob_systemic,
                "prob_receptive": prob_receptive,
                "prob_natural_recovery": prob_natural_recovery,
                "threshold": threshold,
            },
        },
        "baselines": {
            "NO_INTERVENTION": base_ni.report(),
            "SIMPLE_RULE": base_sr.report(),
        },
        "recoverai": recoverai_metrics.report(),
    }


def main():
    print("Running SENSITIVITY MATRIX...")
    os.makedirs("docs/reports/package-25", exist_ok=True)

    matrix = [
        # BASELINE
        (
            "BASELINE",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.15,
                "threshold": 3,
            },
        ),
        # NATURAL RECOVERY
        (
            "NAT_REC_LOW",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.10,
                "threshold": 3,
            },
        ),
        (
            "NAT_REC_HIGH",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.20,
                "threshold": 3,
            },
        ),
        # SYSTEMIC
        (
            "SYS_LOW",
            {
                "prob_systemic": 0.05,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.15,
                "threshold": 3,
            },
        ),
        (
            "SYS_HIGH",
            {
                "prob_systemic": 0.15,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.15,
                "threshold": 3,
            },
        ),
        # RECEPTIVITY
        (
            "REC_LOW",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.50,
                "prob_natural_recovery": 0.15,
                "threshold": 3,
            },
        ),
        (
            "REC_HIGH",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.70,
                "prob_natural_recovery": 0.15,
                "threshold": 3,
            },
        ),
        # THRESHOLD
        (
            "THRESH_2",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.15,
                "threshold": 2,
            },
        ),
        (
            "THRESH_4",
            {
                "prob_systemic": 0.10,
                "prob_receptive": 0.60,
                "prob_natural_recovery": 0.15,
                "threshold": 4,
            },
        ),
    ]

    results = {}
    for name, kwargs in matrix:
        print(f"  -> Running {name}...")
        results[name] = run_one_evaluation(**kwargs)

    with open("docs/reports/package-25/p25_sensitivity_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Running FINAL BENCHMARK ONCE...")
    baseline_result = results["BASELINE"]
    with open("docs/reports/package-25/p25_baseline_results.json", "w") as f:
        json.dump(baseline_result, f, indent=2)


if __name__ == "__main__":
    main()
