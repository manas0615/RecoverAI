import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app

client = TestClient(app)


def test_analyze_case_plan_none():
    """Test that analyze_case works even if plan is None (P22 regression fix)."""
    # Create an active case
    from datetime import UTC, datetime

    from recoverai.domain.case import RecoveryCase, RecoveryCaseId, RevenueSource
    from recoverai.domain.identifiers import CustomerId, MerchantId, RevenueEventId
    from recoverai.domain.money import CurrencyCode, Money, RevenueAmount

    case = RecoveryCase(
        case_id=RecoveryCaseId("test_case_analyze_1"),
        merchant_id=MerchantId("merch_1"),
        customer_id=CustomerId("cust_1"),
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.USD)),
        revenue_source=RevenueSource.PAYMENT,
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
    )

    with pytest.MonkeyPatch.context() as m:
        from recoverai.api.main import container
        from recoverai.domain.assessment import (
            AnalysisType,
            CauseAssessment,
            Probability,
            RiskAssessment,
        )
        from recoverai.domain.money import CurrencyCode, Money, RevenueAmount

        # We need a case in the DB to avoid 404, or mock RecoveryCaseRepository.get
        class MockCaseRepo:
            def __init__(self, conn):
                pass

            def get(self, cid):
                return case

            def save(self, case):
                pass

        from recoverai.api import main

        m.setattr(main, "RecoveryCaseRepository", MockCaseRepo)

        # We also need to mock RevenueEventRepository.get
        class MockEventRepo:
            def __init__(self, conn):
                pass

            def get(self, eid):
                return None

        m.setattr(main, "RevenueEventRepository", MockEventRepo)

        case_id_val = "test_case_analyze_1"

        def mock_analyze(c, events, **kwargs):
            risk = RiskAssessment(
                assessment_id="risk_1",
                case_id=c.case_id,
                recovery_probability=Probability(0.5, "Mock"),
                expected_recovery_value=RevenueAmount(Money(500, CurrencyCode.USD)),
                model_name="test_model",
                model_version="1.0",
                created_at=datetime.now(UTC),
            )
            cause = CauseAssessment(
                cause_assessment_id="cause_1",
                case_id=c.case_id,
                analysis_type=AnalysisType.RULE_BASED,
                category="INSUFFICIENT_FUNDS",
                confidence=Probability(0.9, "Mock"),
                model_version="1.0",
                created_at=datetime.now(UTC),
            )
            return risk, cause, None

        m.setattr(container.intelligence, "analyze", mock_analyze)

        def mock_evaluate(*args, **kwargs):
            class MockDecisionValue:
                value = "DENY"

            class MockDecision:
                decision = MockDecisionValue()
                reason_codes = ("MOCK_POLICY",)

            return MockDecision()

        m.setattr(container.policy, "evaluate", mock_evaluate)

        response = client.post(
            f"/recovery-cases/{case_id_val}/analyze",
            headers={"X-API-Key": "test_frontend_key_default"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["recommendation"] == "UNKNOWN"
        assert data["expected_recovery_value"] == 500
        assert data["recovery_probability"] == 0.5
        assert data["cause_category"] == "INSUFFICIENT_FUNDS"


def test_closed_case_mutate():
    from datetime import UTC, datetime

    from recoverai.domain.case import (
        CaseWorkflowState,
        RecoveryCase,
        RecoveryCaseId,
        RecoveryCaseStatus,
        RecoveryOutcomeValue,
        RevenueSource,
    )
    from recoverai.domain.identifiers import CustomerId, MerchantId, RevenueEventId
    from recoverai.domain.money import CurrencyCode, Money, RevenueAmount

    case = RecoveryCase(
        case_id=RecoveryCaseId("test_case_closed"),
        merchant_id=MerchantId("merch_1"),
        customer_id=CustomerId("cust_1"),
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.USD)),
        revenue_source=RevenueSource.PAYMENT,
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
        status=RecoveryCaseStatus.CLOSED,
        workflow_state=CaseWorkflowState.CLOSED,
        outcome_type=RecoveryOutcomeValue.RECOVERED,
    )

    with pytest.MonkeyPatch.context() as m:

        class MockCaseRepo:
            def __init__(self, conn):
                pass

            def get(self, cid):
                return case

        from recoverai.api import main

        m.setattr(main, "RecoveryCaseRepository", MockCaseRepo)

        response = client.post(
            "/recovery-cases/test_case_closed/analyze",
            headers={"X-API-Key": "test_frontend_key_default"},
        )
        assert response.status_code == 400
        assert "Case is closed" in response.json()["detail"]
