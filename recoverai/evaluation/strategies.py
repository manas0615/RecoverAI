from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any

from recoverai.evaluation.simulator import ObservableCaseEvidence
from recoverai.domain.money import RevenueAmount, CurrencyCode, Money
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus, CaseWorkflowState, RevenueSource
from recoverai.domain.identifiers import RecoveryCaseId, MerchantId, CustomerId, RevenueEventId, RecoveryActionId
from recoverai.domain.event import RevenueEvent, RevenueEventType, EventSourceType, EventSource
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.policy.engine import PolicyEngine, PolicyContext
from recoverai.domain.policy import PolicyDecisionValue
from recoverai.domain.action import RecoveryAction, ActionType, ActionStatus
from recoverai.intelligence.gateway import LLMGateway
from recoverai.domain.assessment import CauseAssessment
from recoverai.domain.plan import InterventionCandidate, CandidateStatus
from recoverai.domain.evidence import Probability
from datetime import datetime, UTC


@dataclass
class StrategyDecision:
    action_taken: str
    probability: float
    probability_source: str
    recommendation_source: str
    proposed_action: str = ''


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
        elif evidence.opportunity_amount.amount_minor >= 40000_00:
            action = "ESCALATE"
        else:
            action = "CREATE_PAYMENT_LINK"
            
        return StrategyDecision(
            action_taken=action,
            probability=0.85,
            probability_source="L2_STATIC_PROBABILITY",
            recommendation_source="L2_DETERMINISTIC_RULE"
        )


def build_case_and_events(evidence: ObservableCaseEvidence):
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
        
    action_history = []
    for i in range(evidence.historical_failure_count):
        action_history.append(RecoveryAction(
            action_id=RecoveryActionId(f"act_{i}"),
            case_id=case.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            requested_at=datetime.now(UTC),
            status=ActionStatus.VERIFIED_FAILURE
        ))
        
    return case, events, action_history


class L3CurrentRecoverAI(EvaluationStrategy):
    def __init__(self):
        self.analyzer = RevenueIntelligenceAnalyzer(llm_gateway=None)
        self.policy_engine = PolicyEngine(generate_decision_id=lambda: "dec_123")
        self.policy_context = PolicyContext(
            policy_version="1.0",
            current_time=datetime.now(UTC),
            max_attempts_per_case=3,
            high_value_threshold=RevenueAmount(Money(40000_00, CurrencyCode.INR))
        )

    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        case, events, action_history = build_case_and_events(evidence)
        risk, cause, plan = self.analyzer.analyze(case, events)
        decision = self.policy_engine.evaluate(self.policy_context, case, plan, action_history, cause)
        
        if decision.decision == PolicyDecisionValue.APPROVE:
            action = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
        else:
            action = decision.decision.value
            
        probability = 0.0
        prob_source = "UNKNOWN"
        if plan.candidates:
            probability = plan.candidates[0].expected_recovery_probability.value
            prob_source = "ACTIVE_MODEL"

        proposed = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"

        return StrategyDecision(
            action_taken=action,
            probability=probability,
            probability_source=prob_source,
            recommendation_source="DETERMINISTIC_FALLBACK",
            proposed_action=proposed
        )


class ControlledAIGateway(LLMGateway):
    def synthesize_cause(self, case, events, context) -> CauseAssessment | None:
        return None
        
    def generate_intervention_candidates(self, case, events, context, cause):
        # Controlled AI logic representing something L2 didn't encode.
        # Suppose L2 suppresses fraud. AI ALSO suppresses fraud (smart).
        # Suppose L2 suppresses history >= 3. AI recommends CREATE_PAYMENT_LINK, but Policy blocks.
        # Suppose L2 creates link if amount < 40k. AI creates link.
        # But if it's "network_timeout" and amount is low, AI says "WAIT". (Differs from L2 which creates link).
        
        failure_code = events[0].metadata.get("failure_code")
        downtime = events[0].metadata.get("gateway_downtime")
        amount = case.amount_at_risk.amount_minor
        history = len(events) - 1
        
        action = ActionType.CREATE_PAYMENT_LINK
        if failure_code == "fraud_suspected":
            # AI smartly suppresses fraud too.
            action = ActionType.SUPPRESS
        elif downtime:
            action = ActionType.WAIT
        elif history >= 3:
            # AI unsafe proposal, expecting policy to block
            action = ActionType.CREATE_PAYMENT_LINK 
        elif amount > 50000_00:
            # AI recommends escalation only above 50k, L2 is 40k. L2 escalate, AI create link? 
            # PolicyEngine high_value is 40k. So Policy will block AI anyway!
            action = ActionType.CREATE_PAYMENT_LINK
        elif failure_code == "customer_error":
            # AI perfectly knows to send a payment link
            action = ActionType.CREATE_PAYMENT_LINK
        elif failure_code == "network_timeout":
            # AI smartly recommends WAIT for network timeout
            action = ActionType.WAIT
        else:
            action = ActionType.CREATE_PAYMENT_LINK
            
        candidate = InterventionCandidate(
            candidate_id="ai_cand_1",
            case_id=case.case_id,
            action_type=action,
            expected_recovery_probability=Probability(0.95, "CONTROLLED_AI_MODEL"),
            expected_recovery_value=case.amount_at_risk,
            eligibility_status=CandidateStatus.PROPOSED,
            reason="AI contextual recommendation",
            evidence_references=[]
        )
        return ("ControlledAI", [candidate])


class L3ControlledAIRecoverAI(EvaluationStrategy):
    def __init__(self):
        self.analyzer = RevenueIntelligenceAnalyzer(llm_gateway=ControlledAIGateway())
        self.policy_engine = PolicyEngine(generate_decision_id=lambda: "dec_ai")
        self.policy_context = PolicyContext(
            policy_version="1.0",
            current_time=datetime.now(UTC),
            max_attempts_per_case=3,
            high_value_threshold=RevenueAmount(Money(40000_00, CurrencyCode.INR))
        )

    def evaluate(self, evidence: ObservableCaseEvidence) -> StrategyDecision:
        case, events, action_history = build_case_and_events(evidence)
        risk, cause, plan = self.analyzer.analyze(case, events)
        decision = self.policy_engine.evaluate(self.policy_context, case, plan, action_history, cause)
        
        if decision.decision == PolicyDecisionValue.APPROVE:
            action = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"
        else:
            action = decision.decision.value
            
        probability = 0.0
        prob_source = "UNKNOWN"
        if plan.candidates:
            probability = plan.candidates[0].expected_recovery_probability.value
            prob_source = "ACTIVE_MODEL"

        proposed = plan.selected_action_type.value if plan.selected_action_type else "SUPPRESS"

        return StrategyDecision(
            action_taken=action,
            probability=probability,
            probability_source=prob_source,
            recommendation_source="CONTROLLED_AI_RECOMMENDATION",
            proposed_action=proposed
        )
