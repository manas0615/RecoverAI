from dataclasses import dataclass
from decimal import Decimal

from recoverai.evaluation.metrics import EvaluationMetrics
from recoverai.evaluation.simulator import SyntheticScenario


@dataclass
class ObservedOutcome:
    action_taken: str
    unauthorized_execution_attempt: bool = False
    policy_bypass_attempt: bool = False
    unknown_handled: bool = False
    evidence_mismatch: bool = False
    amount_mismatch: bool = False
    duplicate_evidence: bool = False
    claimed_recovery: bool = False


class Evaluator:
    def __init__(self):
        self.metrics = EvaluationMetrics()
        self.scenarios_evaluated = []

    def _simulate_outcome(
        self, scenario: SyntheticScenario, action_taken: str, metrics: EvaluationMetrics
    ) -> None:
        is_success = False
        is_failed_intervention = False
        amount = Decimal(scenario.evidence.opportunity_amount.amount_minor) / Decimal(
            100
        )

        if action_taken == "CREATE_PAYMENT_LINK":
            metrics.intervention_attempts += 1
            if (
                scenario.truth.receptive_to_intervention
                or scenario.truth.expected_natural_recovery
            ):
                is_success = True
            else:
                is_failed_intervention = True

        elif action_taken == "ESCALATE":
            metrics.escalations += 1
            if scenario.truth.expected_natural_recovery:
                is_success = True

        elif action_taken == "SUPPRESS":
            metrics.suppressions += 1
            if scenario.truth.expected_natural_recovery:
                is_success = True

        if is_success:
            metrics.recovered_cases += 1
            metrics.verified_recovered_revenue += amount

        if is_failed_intervention:
            metrics.failed_interventions += 1

    def evaluate_case(
        self, scenario: SyntheticScenario, observed: ObservedOutcome
    ) -> None:
        amount = Decimal(scenario.evidence.opportunity_amount.amount_minor) / Decimal(
            100
        )
        self.metrics.eligible_recovery_cases += 1
        self.metrics.revenue_at_risk += amount
        self.scenarios_evaluated.append(scenario)

        self._simulate_outcome(scenario, observed.action_taken, self.metrics)

        actual_success = False
        if observed.action_taken == "CREATE_PAYMENT_LINK":
            if (
                scenario.truth.receptive_to_intervention
                or scenario.truth.expected_natural_recovery
            ):
                actual_success = True
        elif scenario.truth.expected_natural_recovery:
            actual_success = True

        if observed.claimed_recovery and not actual_success:
            self.metrics.false_recovery_claims += 1

        if observed.unauthorized_execution_attempt:
            self.metrics.unauthorized_execution_attempts += 1
        if observed.policy_bypass_attempt:
            self.metrics.policy_bypass_attempts += 1
        if observed.unknown_handled:
            self.metrics.unknown_handling_count += 1
        if observed.evidence_mismatch:
            self.metrics.incorrect_evidence_matching += 1
        if observed.amount_mismatch:
            self.metrics.amount_currency_mismatch += 1
        if observed.duplicate_evidence:
            self.metrics.duplicate_evidence_count += 1

    def evaluate_baseline(self, strategy: str) -> EvaluationMetrics:
        baseline = EvaluationMetrics()
        for scenario in self.scenarios_evaluated:
            amount = Decimal(
                scenario.evidence.opportunity_amount.amount_minor
            ) / Decimal(100)
            baseline.eligible_recovery_cases += 1
            baseline.revenue_at_risk += amount

            if strategy == "NO_INTERVENTION":
                self._simulate_outcome(scenario, "SUPPRESS", baseline)

            elif strategy == "SIMPLE_RULE":
                if scenario.evidence.gateway_downtime_active:
                    action = "SUPPRESS"
                else:
                    action = "CREATE_PAYMENT_LINK"
                self._simulate_outcome(scenario, action, baseline)

        return baseline
