import uuid
from datetime import UTC, datetime
from unittest import mock

import pytest

from recoverai.api.main import container
from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.case import (
    RecoveryCase,
    RevenueSource,
)
from recoverai.domain.identifiers import (
    CustomerId,
    MerchantId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.mcp.schemas import ResumeRecoveryActionInput
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository


@pytest.fixture(autouse=True)
def setup_db():
    import os

    container.tm.run_migrations(
        os.path.join(
            os.path.dirname(__file__), "../../recoverai/persistence/migrations"
        )
    )
    from recoverai.config import settings

    settings.razorpay_mode = "test"
    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_demo', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO customers (customer_id, merchant_id, display_name, created_at, updated_at) VALUES ('cust_demo', 'merch_demo', 'Demo Customer', '2023-01-01', '2023-01-01')"
        )


@pytest.fixture
def base_case_and_action():
    case_id = RecoveryCaseId(f"case_approval_{datetime.now(UTC).timestamp()}")
    action_id = RecoveryActionId(f"act_approval_{datetime.now(UTC).timestamp()}")

    with container.tm.transaction() as conn:
        from recoverai.domain.event import (
            EventSource,
            EventSourceType,
            RevenueEvent,
            RevenueEventType,
        )
        from recoverai.persistence.repositories.event import RevenueEventRepository

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

        import json

        from recoverai.domain.evidence import Probability
        from recoverai.domain.plan import (
            CandidateStatus,
            InterventionCandidate,
            InterventionPlan,
        )

        candidate = InterventionCandidate(
            candidate_id="mock_cand",
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            expected_recovery_probability=Probability(value=0.99, meaning="mock"),
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            eligibility_status=CandidateStatus.PROPOSED,
        )

        plan = InterventionPlan(
            plan_id="mock",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="mock",
            selection_model_version="mock",
            expected_recovery_value=RevenueAmount(Money(5000, CurrencyCode.USD)),
            created_at=datetime.now(UTC),
        )

        action = RecoveryAction(
            action_id=action_id,
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.ESCALATED,
            requested_at=datetime.now(UTC),
            plan_snapshot=json.dumps(plan.to_dict()),
        )
        RecoveryActionRepository(conn).save(action)
    return case_id, action_id


@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_resume_approved_human_callback(mock_rzp_urlopen, base_case_and_action):
    case_id, action_id = base_case_and_action

    # 1. Mock execution success
    mock_rzp_urlopen.side_effect = None
    mock_context_manager = mock.MagicMock()
    mock_context_manager.__enter__.return_value.read.return_value = (
        b'{"id":"plink_123"}'
    )
    mock_rzp_urlopen.return_value = mock_context_manager

    # 2. Invoke MCP Tool
    req = ResumeRecoveryActionInput(case_id=case_id.value, action_id=action_id.value)
    result = container.mcp_registry.execute("resume_recovery_action", req.model_dump())

    # 3. Assert execution success
    assert result.get("success") is True
    data = result["data"]
    assert data["status"] == ActionStatus.VERIFICATION_PENDING.name


@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_resume_stale_or_invalid_status(mock_rzp_urlopen, base_case_and_action):
    case_id, action_id = base_case_and_action

    with container.tm.transaction() as conn:
        action = RecoveryActionRepository(conn).get(action_id)
        action.status = ActionStatus.CANCELLED
        RecoveryActionRepository(conn).save(action)

    req = ResumeRecoveryActionInput(case_id=case_id.value, action_id=action_id.value)
    result = container.mcp_registry.execute("resume_recovery_action", req.model_dump())
    assert result.get("success") is not True
    assert result.get("code") == "INVALID_STATE"


@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_resume_terminal_case(mock_rzp_urlopen, base_case_and_action):
    case_id, action_id = base_case_and_action

    with container.tm.transaction() as conn:
        from recoverai.domain.case import RecoveryOutcomeValue

        case = RecoveryCaseRepository(conn).get(case_id)
        case.close(RecoveryOutcomeValue.SUPPRESSED, datetime.now(UTC))
        RecoveryCaseRepository(conn).save(case)

    req = ResumeRecoveryActionInput(case_id=case_id.value, action_id=action_id.value)
    result = container.mcp_registry.execute("resume_recovery_action", req.model_dump())

    assert result.get("success") is not True
    print("TEST_RESUME_TERMINAL_CASE RESULT: ", result)

@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_resume_proposed_action_rejected(mock_rzp_urlopen, base_case_and_action):
    case_id, action_id = base_case_and_action

    with container.tm.transaction() as conn:
        action = RecoveryActionRepository(conn).get(action_id)
        action.status = ActionStatus.PROPOSED
        RecoveryActionRepository(conn).save(action)

    req = ResumeRecoveryActionInput(case_id=case_id.value, action_id=action_id.value)
    result = container.mcp_registry.execute("resume_recovery_action", req.model_dump())
    assert result.get("success") is not True
    assert result.get("code") == "INVALID_STATE"
    assert "PROPOSED" in result.get("error", " ")
