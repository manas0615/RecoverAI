import os
import uuid
from datetime import UTC, datetime
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app, container
from recoverai.config import settings
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.event import EventSource, EventSourceType, RevenueEvent, RevenueEventType
from recoverai.domain.identifiers import RevenueEventId

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    container.tm.run_migrations(
        os.path.join(
            os.path.dirname(__file__), "../../recoverai/persistence/migrations"
        )
    )
    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_1', 'Demo Merchant', 'INR', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )

def _setup_case(amount_minor: int) -> RecoveryCaseId:
    payment_id = f"pay_{uuid.uuid4().hex[:8]}"
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        event = RevenueEvent(
            event_id=RevenueEventId(f"evt_{uuid.uuid4().hex[:8]}"),
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, payment_id),
            merchant_id=MerchantId("merch_1"),
            amount=Money(amount_minor, CurrencyCode.INR),
            occurred_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
        )
        RevenueEventRepository(conn).save(event)
    return container.case_manager.create_or_update_from_event(event).case_id

def test_high_value_escalates_and_does_not_execute(monkeypatch):
    monkeypatch.setattr(settings, "high_value_threshold_inr", 40000_00)
    case_id = _setup_case(50000_00)
    
    from recoverai.domain.assessment import RiskAssessment, CauseAssessment, Probability, AnalysisType
    from recoverai.domain.action import ActionType
    from recoverai.domain.plan import InterventionPlan, InterventionCandidate, CandidateStatus
    
    with mock.patch.object(container.intelligence, "analyze") as mock_analyze:
        mock_risk = RiskAssessment(
            assessment_id="risk_1",
            case_id=case_id,
            recovery_probability=Probability(0.9, "High"),
            expected_recovery_value=RevenueAmount(Money(50000_00, CurrencyCode.INR)),
            model_name="mock",
            model_version="mock",
            created_at=datetime.now(UTC),
        )
        mock_cause = CauseAssessment(
            cause_assessment_id="cause_1",
            case_id=case_id,
            category="INSUFFICIENT_FUNDS",
            confidence=Probability(0.9, "High"),
            analysis_type=AnalysisType.RULE_BASED,
            model_version="mock",
            created_at=datetime.now(UTC),
        )
        candidate = InterventionCandidate(
            candidate_id="mock_cand",
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            expected_recovery_probability=Probability(0.9, "High"),
            expected_recovery_value=RevenueAmount(Money(50000_00, CurrencyCode.INR)),
            eligibility_status=CandidateStatus.PROPOSED,
        )
        mock_plan = InterventionPlan(
            plan_id="mock",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="mock",
            selection_model_version="mock",
            expected_recovery_value=RevenueAmount(Money(50000_00, CurrencyCode.INR)),
            created_at=datetime.now(UTC),
        )
        mock_analyze.return_value = (mock_risk, mock_cause, mock_plan)
        
        with mock.patch.object(container.rzp_adapter, "execute_payment_link") as mock_exec:
            with mock.patch("urllib.request.urlopen"):
                response = client.post(
                    f"/recovery-cases/{case_id.value}/analyze",
                    headers={"X-API-Key": "test_frontend_key_default"},
                )
            
            assert response.status_code == 200
            mock_exec.assert_not_called()
            
            with container.tm.transaction() as conn:
                from recoverai.persistence.repositories.action import RecoveryActionRepository
                action_repo = RecoveryActionRepository(conn)
                actions = action_repo.get_by_case(case_id)
                assert len(actions) == 1
                from recoverai.domain.action import ActionStatus
                assert actions[0].status == ActionStatus.ESCALATED

def test_below_threshold_approves_and_executes(monkeypatch):
    monkeypatch.setattr(settings, "high_value_threshold_inr", 40000_00)
    case_id = _setup_case(10000_00)
    
    from recoverai.domain.assessment import RiskAssessment, CauseAssessment, Probability, AnalysisType
    from recoverai.domain.action import ActionType
    from recoverai.domain.plan import InterventionPlan, InterventionCandidate, CandidateStatus
    
    with mock.patch.object(container.intelligence, "analyze") as mock_analyze:
        mock_risk = RiskAssessment(
            assessment_id="risk_1",
            case_id=case_id,
            recovery_probability=Probability(0.9, "High"),
            expected_recovery_value=RevenueAmount(Money(10000_00, CurrencyCode.INR)),
            model_name="mock",
            model_version="mock",
            created_at=datetime.now(UTC),
        )
        mock_cause = CauseAssessment(
            cause_assessment_id="cause_1",
            case_id=case_id,
            category="INSUFFICIENT_FUNDS",
            confidence=Probability(0.9, "High"),
            analysis_type=AnalysisType.RULE_BASED,
            model_version="mock",
            created_at=datetime.now(UTC),
        )
        candidate = InterventionCandidate(
            candidate_id="mock_cand",
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            expected_recovery_probability=Probability(0.9, "High"),
            expected_recovery_value=RevenueAmount(Money(10000_00, CurrencyCode.INR)),
            eligibility_status=CandidateStatus.PROPOSED,
        )
        mock_plan = InterventionPlan(
            plan_id="mock",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="mock",
            selection_model_version="mock",
            expected_recovery_value=RevenueAmount(Money(10000_00, CurrencyCode.INR)),
            created_at=datetime.now(UTC),
        )
        mock_analyze.return_value = (mock_risk, mock_cause, mock_plan)
        
        from recoverai.integrations.razorpay.adapter import RazorpayExecutionResult, RazorpayExecutionResultType
        with mock.patch.object(container.rzp_adapter, "execute_payment_link") as mock_exec:
            mock_exec.return_value = RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
                provider_reference="plink_mock",
                short_url="http://mock"
            )
            response = client.post(
                f"/recovery-cases/{case_id.value}/analyze",
                headers={"X-API-Key": "test_frontend_key_default"},
            )
            
            assert response.status_code == 200
            mock_exec.assert_called_once()
            
            with container.tm.transaction() as conn:
                from recoverai.persistence.repositories.action import RecoveryActionRepository
                action_repo = RecoveryActionRepository(conn)
                actions = action_repo.get_by_case(case_id)
                assert len(actions) == 1
                from recoverai.domain.action import ActionStatus
                assert actions[0].status == ActionStatus.VERIFICATION_PENDING
