from decimal import Decimal

from recoverai.evaluation.metrics import EvaluationMetrics


class Evaluator:
    def __init__(self):
        self.metrics = EvaluationMetrics()

    def add_case_result(
        self,
        amount: Decimal,
        recovered: bool,
        is_false_recovery: bool = False,
        unauthorized: bool = False,
        policy_bypass: bool = False,
        unknown_handled: bool = False,
        evidence_mismatch: bool = False,
        amount_mismatch: bool = False,
        duplicate: bool = False,
    ) -> None:
        self.metrics.eligible_recovery_cases += 1
        self.metrics.revenue_at_risk += amount

        if recovered and not is_false_recovery:
            self.metrics.recovered_cases += 1
            self.metrics.verified_recovered_revenue += amount

        if is_false_recovery:
            self.metrics.false_recoveries += 1

        if unauthorized:
            self.metrics.unauthorized_execution_attempts += 1

        if policy_bypass:
            self.metrics.policy_bypass_attempts += 1

        if unknown_handled:
            self.metrics.unknown_handling_count += 1

        if evidence_mismatch:
            self.metrics.incorrect_evidence_matching += 1

        if amount_mismatch:
            self.metrics.amount_currency_mismatch += 1

        if duplicate:
            self.metrics.duplicate_evidence_count += 1

    def evaluate_baseline(self, strategy: str) -> EvaluationMetrics:
        """
        Calculates baseline performance (No Intervention, Naive)
        on identical scenario sets to contrast with AI performance.
        For demonstration, returns a frozen static baseline.
        """
        baseline = EvaluationMetrics()
        baseline.eligible_recovery_cases = self.metrics.eligible_recovery_cases
        baseline.revenue_at_risk = self.metrics.revenue_at_risk
        if strategy == "NO_INTERVENTION":
            pass  # 0 recovered
        elif strategy == "NAIVE":
            # Assume 10% naive recovery for synthetic contrast
            baseline.recovered_cases = int(baseline.eligible_recovery_cases * 0.1)
            baseline.verified_recovered_revenue = baseline.revenue_at_risk * Decimal(
                "0.1"
            )
        return baseline
