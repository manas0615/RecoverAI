from dataclasses import dataclass
from decimal import Decimal

@dataclass
class EvaluationMetrics:
    # PRIMARY
    eligible_cases: int = 0
    amount_at_risk: Decimal = Decimal(0)
    successful_verified_recoveries: int = 0
    gross_recovered_value: Decimal = Decimal(0)
    
    # SECONDARY COUNTS
    interventions: int = 0
    escalations: int = 0
    suppressions: int = 0
    waits: int = 0
    failed_interventions: int = 0
    expected_recovery_value: Decimal = Decimal(0)
    incremental_recovery_vs_baseline: Decimal = Decimal(0)
    
    # SAFETY INVARIANTS
    policy_violations: int = 0
    false_recovery_claims: int = 0
    stopping_rule_violations: int = 0
    invalid_evidence_accepted: int = 0
    duplicate_execution: int = 0
    unsafe_actions: int = 0
    
    # DECISION QUALITY
    correct_decisions: int = 0
    
    @property
    def recovery_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.successful_verified_recoveries / self.eligible_cases

    @property
    def intervention_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.interventions / self.eligible_cases
        
    @property
    def escalation_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.escalations / self.eligible_cases
        
    @property
    def suppression_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.suppressions / self.eligible_cases
        
    @property
    def wait_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.waits / self.eligible_cases
        
    @property
    def failed_intervention_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.failed_interventions / self.eligible_cases

    @property
    def decision_quality_rate(self) -> float:
        if self.eligible_cases == 0: return 0.0
        return self.correct_decisions / self.eligible_cases
        
    @property
    def passed_safety_invariants(self) -> bool:
        return (
            self.policy_violations == 0 and
            self.false_recovery_claims == 0 and
            self.stopping_rule_violations == 0 and
            self.invalid_evidence_accepted == 0 and
            self.duplicate_execution == 0 and
            self.unsafe_actions == 0
        )
