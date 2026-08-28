from dataclasses import dataclass
from decimal import Decimal

from recoverai.evaluation.metrics import EvaluationMetrics
from recoverai.evaluation.simulator import SyntheticScenario


@dataclass
class ObservedOutcome:
    action_taken: str | None
    verified_recovered: bool
    unauthorized_execution_attempt: bool = False
    policy_bypass_attempt: bool = False
    unknown_handled: bool = False
    evidence_mismatch: bool = False
    amount_mismatch: bool = False
    duplicate_evidence: bool = False


class Evaluator:
    def __init__(self):
        self.metrics = EvaluationMetrics()
        self.scenarios_evaluated: list[SyntheticScenario] = []

    def evaluate_case(
        self, scenario: SyntheticScenario, observed: ObservedOutcome
    ) -> None:
        amount = Decimal(scenario.opportunity_amount.amount_minor) / Decimal(100)
        self.metrics.eligible_recovery_cases += 1
        self.metrics.revenue_at_risk += amount
        self.scenarios_evaluated.append(scenario)

        # Compare ground truth to observed
        # A false recovery is when the system claims verified recovery, but the ground truth was not receptive
        # and no natural recovery was expected (impossible recovery).
        is_false_recovery = (
            observed.verified_recovered
            and not scenario.receptive_to_intervention
            and not scenario.expected_natural_recovery
        )

        if observed.verified_recovered and not is_false_recovery:
            self.metrics.recovered_cases += 1
            self.metrics.verified_recovered_revenue += amount

        if is_false_recovery:
            self.metrics.false_recoveries += 1

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
        """
        Calculates baseline performance explicitly across the exact same scenarios
        evaluated by this instance.

        NO_INTERVENTION: Models 0% active recovery. Relies strictly on expected_natural_recovery.
        NAIVE: Models a static 10% recovery rule ignoring systemic degradation, directly penalized by false recoveries.
        """
        baseline = EvaluationMetrics()
        for scenario in self.scenarios_evaluated:
            amount = Decimal(scenario.opportunity_amount.amount_minor) / Decimal(100)
            baseline.eligible_recovery_cases += 1
            baseline.revenue_at_risk += amount

            if strategy == "NO_INTERVENTION":
                if scenario.expected_natural_recovery:
                    baseline.recovered_cases += 1
                    baseline.verified_recovered_revenue += amount

            elif strategy == "NAIVE":
                # Naive attempts action on everything
                # It recovers if the customer is receptive
                if (
                    scenario.receptive_to_intervention
                    or scenario.expected_natural_recovery
                ):
                    baseline.recovered_cases += 1
                    baseline.verified_recovered_revenue += amount
                else:
                    # Naive might cause problems, but we'll strictly log it as not recovered
                    pass
        return baseline
