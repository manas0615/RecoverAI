import uuid
from datetime import UTC, datetime
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app, container
from recoverai.domain.action import ActionType
from recoverai.domain.assessment import AnalysisType, CauseAssessment, RiskAssessment
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.event import (
    EventSource,
    EventSourceType,
    RevenueEvent,
    RevenueEventType,
)
from recoverai.domain.evidence import Probability
from recoverai.domain.identifiers import (
    CustomerId,
    MerchantId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.plan import (
    CandidateStatus,
    InterventionCandidate,
    InterventionPlan,
)
from recoverai.mcp.schemas import CreatePaymentLinkInput
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    import os

    container.tm.run_migrations(
        os.path.join(
            os.path.dirname(__file__), "../../recoverai/persistence/migrations"
        )
    )
    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_demo', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO customers (customer_id, merchant_id, display_name, created_at, updated_at) VALUES ('cust_demo', 'merch_demo', 'Demo Customer', '2023-01-01', '2023-01-01')"
        )


@pytest.fixture
def base_case():
    case_id = RecoveryCaseId(f"case_sys_{datetime.now(UTC).timestamp()}")

    with container.tm.transaction() as conn:
        event_id = RevenueEventId(f"evt_{datetime.now(UTC).timestamp()}")
        payment_id = f"pay_{uuid.uuid4().hex[:8]}"
        event = RevenueEvent(
            event_id=event_id,
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, payment_id),
            merchant_id=MerchantId("merch_demo"),
            amount=Money(5000, CurrencyCode.USD),
            occurred_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
        )
        RevenueEventRepository(conn).save(event)

        case = RecoveryCase(
            case_id=case_id,
            merchant_id=MerchantId("merch_demo"),
            customer_id=CustomerId("cust_demo"),
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.USD)),
            opened_at=datetime.now(UTC),
            source_event_ids={event_id},
        )
        RecoveryCaseRepository(conn).save(case)
    return case_id


def test_analyze_path_systemic_degradation(base_case):
    case_id = base_case

    # Mock intelligence to return SYSTEMIC_DEGRADATION cause
    with mock.patch.object(container.intelligence, "analyze") as mock_analyze:
        mock_risk = RiskAssessment(
            assessment_id="risk_1",
            case_id=case_id,
            recovery_probability=Probability(0.2, "Low"),
            expected_recovery_value=RevenueAmount(Money(1000, CurrencyCode.USD)),
            model_name="mock",
            model_version="mock",
            created_at=datetime.now(UTC),
        )
        mock_cause = CauseAssessment(
            cause_assessment_id="cause_1",
            case_id=case_id,
            category="SYSTEMIC_DEGRADATION",
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
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            eligibility_status=CandidateStatus.PROPOSED,
        )
        mock_plan = InterventionPlan(
            plan_id="mock",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="mock",
            selection_model_version="mock",
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            created_at=datetime.now(UTC),
        )
        mock_analyze.return_value = (mock_risk, mock_cause, mock_plan)

        response = client.post(
            f"/recovery-cases/{case_id.value}/analyze",
            headers={"X-API-Key": "test_frontend_key_default"},
        )
        assert response.status_code == 200

        from recoverai.persistence.repositories.audit import AuditRepository

        with container.tm.transaction() as conn:
            audit_events = [
                ae
                for ae in AuditRepository(conn).get_by_case(case_id.value)
                if ae.event_type.value == "POLICY_DECISION_CREATED"
            ]
            data = audit_events[0].metadata

        assert data["decision"] == "SUPPRESS"
        assert "SYSTEMIC_DEGRADATION" in data["reasons"]


@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_create_payment_link_execution_path(mock_rzp_urlopen, base_case):
    case_id = base_case

    # Mock intelligence to return SYSTEMIC_DEGRADATION cause
    with mock.patch.object(
        container.mcp_context.intelligence, "analyze"
    ) as mock_analyze:
        mock_risk = RiskAssessment(
            assessment_id="risk_1",
            case_id=case_id,
            recovery_probability=Probability(0.2, "Low"),
            expected_recovery_value=RevenueAmount(Money(1000, CurrencyCode.USD)),
            model_name="mock",
            model_version="mock",
            created_at=datetime.now(UTC),
        )
        mock_cause = CauseAssessment(
            cause_assessment_id="cause_1",
            case_id=case_id,
            category="SYSTEMIC_DEGRADATION",
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
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            eligibility_status=CandidateStatus.PROPOSED,
        )
        mock_plan = InterventionPlan(
            plan_id="mock",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="mock",
            selection_model_version="mock",
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            created_at=datetime.now(UTC),
        )
        mock_analyze.return_value = (mock_risk, mock_cause, mock_plan)

        req = CreatePaymentLinkInput(
            case_id=case_id.value, action_id=f"act_{datetime.now(UTC).timestamp()}"
        )

        # Result should be policy denial because of systemic degradation SUPPRESS
        result = container.mcp_registry.execute("create_payment_link", req.model_dump())
        assert result.get("success") is not True
        assert result.get("code") == "POLICY_DENIAL"

        # Verify Razorpay was NOT contacted
        mock_rzp_urlopen.assert_not_called()


def test_non_systemic_regression(base_case):
    case_id = base_case

    # Mock intelligence to return NORMAL cause
    with (
        mock.patch.object(container.intelligence, "analyze") as mock_analyze,
        mock.patch.object(container.rzp_adapter, "execute_payment_link") as mock_exec,
    ):
        from recoverai.integrations.razorpay.adapter import (
            RazorpayExecutionResult,
            RazorpayExecutionResultType,
        )

        mock_exec.return_value = RazorpayExecutionResult(
            result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
            provider_reference="plink_mocked_sys",
            short_url="https://rzp.io/i/sysmock",
        )
        mock_risk = RiskAssessment(
            assessment_id="risk_1",
            case_id=case_id,
            recovery_probability=Probability(0.9, "High"),
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
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
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            eligibility_status=CandidateStatus.PROPOSED,
        )
        mock_plan = InterventionPlan(
            plan_id="mock",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="mock",
            selection_model_version="mock",
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            created_at=datetime.now(UTC),
        )
        mock_analyze.return_value = (mock_risk, mock_cause, mock_plan)

        response = client.post(
            f"/recovery-cases/{case_id.value}/analyze",
            headers={"X-API-Key": "test_frontend_key_default"},
        )
        assert response.status_code == 200

        from recoverai.persistence.repositories.audit import AuditRepository

        with container.tm.transaction() as conn:
            audit_events = [
                ae
                for ae in AuditRepository(conn).get_by_case(case_id.value)
                if ae.event_type.value == "POLICY_DECISION_CREATED"
            ]
            data = audit_events[0].metadata

        assert data["decision"] == "APPROVE"
        assert "POLICY_APPROVED" in data["reasons"]
