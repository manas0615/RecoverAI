from dataclasses import dataclass
from decimal import Decimal


@dataclass
class EvaluationMetrics:
    revenue_at_risk: Decimal = Decimal(0)
    verified_recovered_revenue: Decimal = Decimal(0)
    eligible_recovery_cases: int = 0
    recovered_cases: int = 0

    intervention_attempts: int = 0
    failed_interventions: int = 0
    false_recovery_claims: int = 0
    escalations: int = 0
    suppressions: int = 0

    unauthorized_execution_attempts: int = 0
    policy_bypass_attempts: int = 0
    unknown_handling_count: int = 0
    incorrect_evidence_matching: int = 0
    amount_currency_mismatch: int = 0
    duplicate_evidence_count: int = 0

    @property
    def revenue_recovery_rate(self) -> Decimal:
        if self.revenue_at_risk == Decimal(0):
            return Decimal(0)
        return self.verified_recovered_revenue / self.revenue_at_risk

    @property
    def case_recovery_rate(self) -> Decimal:
        if self.eligible_recovery_cases == 0:
            return Decimal(0)
        return Decimal(self.recovered_cases) / Decimal(self.eligible_recovery_cases)

    def report(self) -> dict:
        return {
            "revenue_at_risk": float(self.revenue_at_risk),
            "verified_recovered_revenue": float(self.verified_recovered_revenue),
            "revenue_recovery_rate": float(self.revenue_recovery_rate),
            "eligible_recovery_cases": self.eligible_recovery_cases,
            "recovered_cases": self.recovered_cases,
            "case_recovery_rate": float(self.case_recovery_rate),
            "interventions": {
                "attempts": self.intervention_attempts,
                "failed": self.failed_interventions,
                "escalations": self.escalations,
                "suppressions": self.suppressions,
            },
            "safety": {
                "false_recovery_claims": self.false_recovery_claims,
                "unauthorized_execution_attempts": self.unauthorized_execution_attempts,
                "policy_bypass_attempts": self.policy_bypass_attempts,
                "unknown_handling_count": self.unknown_handling_count,
                "incorrect_evidence_matching": self.incorrect_evidence_matching,
                "amount_currency_mismatch": self.amount_currency_mismatch,
                "duplicate_evidence_count": self.duplicate_evidence_count,
            },
        }
