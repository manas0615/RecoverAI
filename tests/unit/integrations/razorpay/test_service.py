from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.identifiers import (
    MerchantId,
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue
from recoverai.integrations.razorpay.adapter import (
    RazorpayAdapter,
    RazorpayExecutionResult,
    RazorpayExecutionResultType,
)
from recoverai.integrations.razorpay.service import RazorpayExecutionService
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository


@pytest.fixture
def adapter() -> MagicMock:
    return MagicMock(spec=RazorpayAdapter)


@pytest.fixture
def valid_case() -> RecoveryCase:
    return RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(5000, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
    )


@pytest.fixture
def valid_action(valid_case: RecoveryCase) -> RecoveryAction:
    return RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=valid_case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=datetime.now(UTC),
        status=ActionStatus.AUTHORIZED,
        attempt_number=1,
    )


@pytest.fixture
def valid_decision() -> PolicyDecision:
    return PolicyDecision(
        policy_decision_id=PolicyDecisionId("pd_1"),
        case_id=RecoveryCaseId("case_1"),
        action_id_or_proposal_id="act_1",
        decision=PolicyDecisionValue.APPROVE,
        policy_version="1.0",
        evaluated_at=datetime.now(UTC),
    )


def test_service_successful_request(
    tm: TransactionManager,
    adapter: MagicMock,
    valid_action: RecoveryAction,
    valid_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    adapter.execute_payment_link.return_value = RazorpayExecutionResult(
        result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
        provider_reference="plink_123",
        short_url="http://rzp/123",
    )

    with tm.transaction() as conn:
        conn.execute(
            "INSERT INTO revenue_events (event_id, event_type, source_type, merchant_id, occurred_at, received_at, metadata, schema_version) VALUES ('evt_1', 'PAYMENT_FAILED', 'WEBHOOK', 'm_1', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', '{}', '1.0')"
        )
        case_repo = RecoveryCaseRepository(conn)
        case_repo.save(valid_case)

        action_repo = RecoveryActionRepository(conn)
        # Need to insert initial action so we don't violate optimistic locking in repo.save (which is UPSERT actually, so it's fine)
        service = RazorpayExecutionService(adapter, action_repo)
        result = service.execute_and_record(valid_action, valid_case, valid_decision)

        assert result.result_type == RazorpayExecutionResultType.SUCCESSFUL_REQUEST

        # Verify persistence
        saved_action = action_repo.get(valid_action.action_id)
        assert saved_action is not None
        assert saved_action.status == ActionStatus.VERIFICATION_PENDING
        assert saved_action.external_reference == "plink_123"


def test_service_timeout_unknown(
    tm: TransactionManager,
    adapter: MagicMock,
    valid_action: RecoveryAction,
    valid_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    adapter.execute_payment_link.return_value = RazorpayExecutionResult(
        result_type=RazorpayExecutionResultType.TIMEOUT_UNKNOWN,
        error_message="Timeout",
    )

    with tm.transaction() as conn:
        conn.execute(
            "INSERT INTO revenue_events (event_id, event_type, source_type, merchant_id, occurred_at, received_at, metadata, schema_version) VALUES ('evt_1', 'PAYMENT_FAILED', 'WEBHOOK', 'm_1', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', '{}', '1.0')"
        )
        case_repo = RecoveryCaseRepository(conn)
        case_repo.save(valid_case)

        action_repo = RecoveryActionRepository(conn)
        service = RazorpayExecutionService(adapter, action_repo)
        result = service.execute_and_record(valid_action, valid_case, valid_decision)

        assert result.result_type == RazorpayExecutionResultType.TIMEOUT_UNKNOWN

        saved_action = action_repo.get(valid_action.action_id)
        assert saved_action is not None
        assert saved_action.status == ActionStatus.EXECUTION_UNKNOWN
        assert saved_action.failure_reason == "Timeout"


def test_service_provider_rejected(
    tm: TransactionManager,
    adapter: MagicMock,
    valid_action: RecoveryAction,
    valid_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    adapter.execute_payment_link.return_value = RazorpayExecutionResult(
        result_type=RazorpayExecutionResultType.PROVIDER_REJECTED,
        error_message="HTTP 400",
    )

    with tm.transaction() as conn:
        conn.execute(
            "INSERT INTO revenue_events (event_id, event_type, source_type, merchant_id, occurred_at, received_at, metadata, schema_version) VALUES ('evt_1', 'PAYMENT_FAILED', 'WEBHOOK', 'm_1', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', '{}', '1.0')"
        )
        case_repo = RecoveryCaseRepository(conn)
        case_repo.save(valid_case)

        action_repo = RecoveryActionRepository(conn)
        service = RazorpayExecutionService(adapter, action_repo)
        result = service.execute_and_record(valid_action, valid_case, valid_decision)

        assert result.result_type == RazorpayExecutionResultType.PROVIDER_REJECTED

        saved_action = action_repo.get(valid_action.action_id)
        assert saved_action is not None
        assert saved_action.status == ActionStatus.VERIFICATION_PENDING
        assert saved_action.failure_reason == "HTTP 400"


def test_service_failed_before_send(
    tm: TransactionManager,
    adapter: MagicMock,
    valid_action: RecoveryAction,
    valid_case: RecoveryCase,
    valid_decision: PolicyDecision,
):
    adapter.execute_payment_link.return_value = RazorpayExecutionResult(
        result_type=RazorpayExecutionResultType.FAILED_BEFORE_SEND,
        error_message="Test mode error",
    )

    with tm.transaction() as conn:
        conn.execute(
            "INSERT INTO revenue_events (event_id, event_type, source_type, merchant_id, occurred_at, received_at, metadata, schema_version) VALUES ('evt_1', 'PAYMENT_FAILED', 'WEBHOOK', 'm_1', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00', '{}', '1.0')"
        )
        case_repo = RecoveryCaseRepository(conn)
        case_repo.save(valid_case)

        action_repo = RecoveryActionRepository(conn)
        service = RazorpayExecutionService(adapter, action_repo)
        result = service.execute_and_record(valid_action, valid_case, valid_decision)

        assert result.result_type == RazorpayExecutionResultType.FAILED_BEFORE_SEND

        saved_action = action_repo.get(valid_action.action_id)
        assert saved_action is not None
        assert saved_action.status == ActionStatus.ESCALATED
        assert saved_action.failure_reason == "Test mode error"
