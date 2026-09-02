from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from recoverai.evaluation.simulator import ObservableCaseEvidence
from recoverai.domain.money import RevenueAmount, CurrencyCode, Money
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus, CaseWorkflowState, RevenueSource
from recoverai.domain.identifiers import RecoveryCaseId, MerchantId, CustomerId, RevenueEventId
from recoverai.domain.event import RevenueEvent, RevenueEventType, EventSourceType, EventSource
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.policy.engine import PolicyEngine, PolicyContext
from recoverai.domain.policy import PolicyDecisionValue
from datetime import datetime, UTC


@dataclass
class StrategyDecision:
    action_taken: str
    probability: float
    probability_source: str
    recommendation_source: str


class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        pass


class L0NoIntervention(EvaluationStrategy):
    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        return StrategyDecision(
            action_taken="SUPPRESS",
            probability=0.0,
            probability_source="L0_STATIC",
            recommendation_source="L0_STATIC"
        )


class L1NaiveRule(EvaluationStrategy):
    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        return StrategyDecision(
            action_taken="CREATE_PAYMENT_LINK",
            probability=1.0,
            probability_source="L1_STATIC",
            recommendation_source="L1_STATIC"
        )


class L2DeterministicRules(EvaluationStrategy):
    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        if evidence.failure_code == "fraud_suspected":
            action = "SUPPRESS"
        elif evidence.gateway_downtime_active:
            action = "WAIT"
        elif evidence.historical_failure_count >= 3:
            action = "SUPPRESS"
        elif evidence.opportunity_amount.amount_minor > 40000_00:
            action = "ESCALATE"
        else:
            action = "CREATE_PAYMENT_LINK"
            
        return StrategyDecision(
            action_taken=action,
            probability=0.85,
            probability_source="L2_STATIC_PROBABILITY",
            recommendation_source="L2_DETERMINISTIC_RULE"
        )


class L3CurrentRecoverAI(EvaluationStrategy):
    def __init__(self):
        self.analyzer = RevenueIntelligenceAnalyzer(llm_gateway=None)
        self.policy_engine = PolicyEngine(generate_decision_id=lambda: "dec_123")
        self.policy_context = PolicyContext(
            policy_version="1.0",
            current_time=datetime.now(UTC),
            max_attempts_per_case=3,
            high_value_threshold=Money(40000_00, CurrencyCode.INR)
        )

    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        # Reconstruct minimal domain models for analyzer
        case = RecoveryCase(
            case_id=RecoveryCaseId(evidence.scenario_id),
            merchant_id=MerchantId(evidence.merchant_id),
            customer_id=CustomerId(evidence.customer_id),
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(evidence.opportunity_amount.amount_minor, CurrencyCode.INR)),
            opened_at=datetime.now(UTC),
            source_event_ids={RevenueEventId("evt_0")},
            status=RecoveryCaseStatus.OPEN,
            workflow_state=CaseWorkflowState.ASSESSED,
            version=1
        )
        
        events = []
        for i in range(evidence.historical_failure_count + 1):
            events.append(RevenueEvent(
                event_id=RevenueEventId(f"evt_{i}"),
                merchant_id=MerchantId(evidence.merchant_id),
                event_type=RevenueEventType.PAYMENT_FAILED,
                source=EventSource(source_type=EventSourceType.SIMULATION),
                metadata={"failure_code": evidence.failure_code, "gateway_downtime": evidence.gateway_downtime_active},
                occurred_at=datetime.now(UTC),
                received_at=datetime.now(UTC)
            ))
            
        risk, cause, plan = self.analyzer.analyze(case, events)
        decision = self.policy_engine.evaluate(self.policy_context, case, plan, [], cause)
        
        # Map policy decision to action
        if decision.decision == PolicyDecisionValue.APPROVE:
            action = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
        else:
            action = decision.decision.value
            
        probability = 0.0
        prob_source = "UNKNOWN"
        if plan.candidates:
            probability = plan.candidates[0].expected_recovery_probability.value
            prob_source = "ACTIVE_MODEL"

        return StrategyDecision(
            action_taken=action,
            probability=probability,
            probability_source=prob_source,
            recommendation_source="DETERMINISTIC_FALLBACK" # Since llm_gateway=None
        )
