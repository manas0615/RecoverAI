import pytest
from datetime import datetime, UTC
from typing import Any

from recoverai.domain.action import ActionType
from recoverai.domain.assessment import AnalysisType, CauseAssessment, RiskAssessment
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.event import RevenueEvent
from recoverai.domain.evidence import EvidenceReference, Probability
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.plan import (
    CandidateStatus,
    InterventionCandidate,
    InterventionPlan,
)
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer
from recoverai.intelligence.gateway import LLMGateway


def create_dummy_case() -> RecoveryCase:
    return RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("merch_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(100, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
    )


from recoverai.domain.event import (
    RevenueEvent,
    RevenueEventType,
    EventSource,
    EventSourceType,
)


def create_dummy_event() -> RevenueEvent:
    return RevenueEvent(
        event_id=RevenueEventId("evt_1"),
        merchant_id=MerchantId("merch_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK),
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        metadata={},
    )


class MockLLMGateway(LLMGateway):
    def synthesize_cause(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
    ) -> CauseAssessment | None:
        if context.get("fail_cause"):
            return None
        return CauseAssessment(
            cause_assessment_id="cause_mock",
            case_id=case.case_id,
            category="MOCK_CATEGORY",
            confidence=Probability(0.95, "mock cause"),
            analysis_type=AnalysisType.LLM,
            model_version="mock_1.0",
            created_at=datetime.now(UTC),
            evidence_references=[],
        )

    def generate_intervention_candidates(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
        cause: CauseAssessment,
    ) -> list[InterventionCandidate]:
        if context.get("fail_candidates"):
            raise ValueError("Mock failure")
        return [
            InterventionCandidate(
                candidate_id="cand_mock",
                case_id=case.case_id,
                action_type=ActionType.WAIT,
                expected_recovery_probability=Probability(0.99, "mock cand prob"),
                expected_recovery_value=case.amount_at_risk,
                eligibility_status=CandidateStatus.PROPOSED,
                reason="Mock generated",
            )
        ]


def test_deterministic_analyzer_systemic():
    analyzer = RevenueIntelligenceAnalyzer()
    case = create_dummy_case()
    event = create_dummy_event()
    context = {"active_downtime": True}

    risk, cause, plan = analyzer.analyze(case, [event], context)

    assert isinstance(risk, RiskAssessment)
    assert risk.recovery_probability.value == 0.1
    assert risk.model_name == "deterministic_baseline"

    assert isinstance(cause, CauseAssessment)
    assert cause.category == "SYSTEMIC_DEGRADATION"

    assert isinstance(plan, InterventionPlan)
    assert len(plan.candidates) == 1
    assert plan.candidates[0].action_type == ActionType.WAIT
    assert plan.selected_action_type == ActionType.WAIT


def test_deterministic_analyzer_customer():
    analyzer = RevenueIntelligenceAnalyzer()
    case = create_dummy_case()
    event = create_dummy_event()
    context = {"active_downtime": False}

    risk, cause, plan = analyzer.analyze(case, [event], context)

    assert risk.recovery_probability.value == 0.8
    assert cause.category == "CUSTOMER_SPECIFIC"
    assert plan.selected_action_type == ActionType.CREATE_PAYMENT_LINK

    # Verify evidence grounding
    assert len(cause.evidence_references) == 1
    assert cause.evidence_references[0].source_id == "evt_1"


def test_mock_llm_analyzer_success():
    analyzer = RevenueIntelligenceAnalyzer(llm_gateway=MockLLMGateway())
    case = create_dummy_case()
    event = create_dummy_event()

    risk, cause, plan = analyzer.analyze(case, [event], {})

    # Risk is still deterministic
    assert risk.recovery_probability.value == 0.8

    # Cause should be from mock LLM
    assert cause.category == "MOCK_CATEGORY"
    assert cause.analysis_type == AnalysisType.LLM

    # Plan should be from mock LLM
    assert len(plan.candidates) == 1
    assert plan.candidates[0].action_type == ActionType.WAIT
    assert plan.selected_action_type == ActionType.WAIT


def test_mock_llm_analyzer_cause_fallback():
    analyzer = RevenueIntelligenceAnalyzer(llm_gateway=MockLLMGateway())
    case = create_dummy_case()
    event = create_dummy_event()

    # Tell mock to fail cause synthesis
    risk, cause, plan = analyzer.analyze(case, [event], {"fail_cause": True})

    # Cause should fall back to deterministic
    assert cause.category == "CUSTOMER_SPECIFIC"
    assert cause.analysis_type == AnalysisType.RULE_BASED

    # Plan still runs against mock because candidates didn't fail
    assert len(plan.candidates) == 1
    assert plan.candidates[0].action_type == ActionType.WAIT


def test_mock_llm_analyzer_candidates_fallback():
    analyzer = RevenueIntelligenceAnalyzer(llm_gateway=MockLLMGateway())
    case = create_dummy_case()
    event = create_dummy_event()

    # Tell mock to throw exception during candidate gen
    risk, cause, plan = analyzer.analyze(case, [event], {"fail_candidates": True})

    # Cause is mock
    assert cause.category == "MOCK_CATEGORY"

    # Plan falls back to deterministic using the mock cause!
    assert len(plan.candidates) == 1
    # Deterministic fallback sees category != SYSTEMIC_DEGRADATION, defaults to CREATE_PAYMENT_LINK
    assert plan.candidates[0].action_type == ActionType.CREATE_PAYMENT_LINK
    assert plan.selected_action_type == ActionType.CREATE_PAYMENT_LINK
