import os
import tempfile
from datetime import UTC, datetime

import pytest

from recoverai.domain import (
    ActionStatus,
    ActionType,
    CaseWorkflowState,
    CurrencyCode,
    EventSource,
    EventSourceType,
    MerchantId,
    Money,
    RecoveryAction,
    RecoveryActionId,
    RecoveryCase,
    RecoveryCaseId,
    RecoveryOutcomeValue,
    RevenueAmount,
    RevenueEvent,
    RevenueEventId,
    RevenueEventType,
    RevenueSource,
)
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository
from recoverai.persistence.repositories.verification import VerificationRecordRepository
from recoverai.verification.engine import VerificationEngine


@pytest.fixture
def tm():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    manager = TransactionManager(f"sqlite:///{path}")
    manager.run_migrations()
    yield manager
    try:
        os.remove(path)
    except:
        pass


@pytest.fixture
def connection(tm):
    conn = tm.create_connection()
    yield conn
    conn.close()


@pytest.fixture
def repos(connection):
    return (
        RecoveryActionRepository(connection),
        RecoveryCaseRepository(connection),
        RevenueEventRepository(connection),
        VerificationRecordRepository(connection),
    )


@pytest.fixture
def engine(repos):
    return VerificationEngine(*repos)


def create_case(case_id: str = "c1") -> RecoveryCase:
    return RecoveryCase(
        case_id=RecoveryCaseId(case_id),
        merchant_id=MerchantId("m1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("e1")},
        workflow_state=CaseWorkflowState.VERIFYING,
    )


def setup_case_and_merchant(connection, event_repo, case_repo):
    connection.execute(
        "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        ("m1", "M", "INR", "ACTIVE", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    event_repo.save(
        RevenueEvent(
            event_id=RevenueEventId("e1"),
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "wh_init"),
            merchant_id=MerchantId("m1"),
            occurred_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
            amount=Money(1000, CurrencyCode.INR),
            metadata={},
        )
    )
    case = create_case()
    case_repo.save(case)
    return case


def test_execution_unknown_no_events_remains_unknown(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        idempotency_key="hash_123",
        status=ActionStatus.EXECUTION_UNKNOWN,
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.EXECUTION_UNKNOWN
    updated_case = case_repo.get(case.case_id)
    assert updated_case.workflow_state == CaseWorkflowState.VERIFYING


def test_verified_failure_when_provider_rejects_synchronously(
    connection, engine, repos
):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.VERIFICATION_PENDING,
        failure_reason="HTTP 400",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.VERIFIED_FAILURE

    updated_case = case_repo.get(case.case_id)
    assert updated_case.workflow_state == CaseWorkflowState.PLANNING


def test_verified_success_when_payment_link_paid(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.VERIFICATION_PENDING,
        external_reference="plink_123",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("evt1"),
        event_type=RevenueEventType.PAYMENT_LINK_PAID,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "wh1"),
        merchant_id=case.merchant_id,
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        amount=Money(1000, CurrencyCode.INR),
        external_reference="plink_123",
        metadata={},
    )
    event_repo.save(event)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.VERIFIED_SUCCESS

    updated_case = case_repo.get(case.case_id)
    assert updated_case.workflow_state == CaseWorkflowState.CLOSED
    assert updated_case.outcome_type == RecoveryOutcomeValue.RECOVERED


def test_verified_success_from_execution_unknown(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.EXECUTION_UNKNOWN,
        idempotency_key="my_hash",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("evt1"),
        event_type=RevenueEventType.PAYMENT_LINK_PAID,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "wh1"),
        merchant_id=case.merchant_id,
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        amount=Money(1000, CurrencyCode.INR),
        external_reference="plink_123",
        metadata={"payload": {"payment_link": {"entity": {"reference_id": "my_hash"}}}},
    )
    event_repo.save(event)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.VERIFIED_SUCCESS
    updated_case = case_repo.get(case.case_id)
    assert updated_case.outcome_type == RecoveryOutcomeValue.RECOVERED


def test_amount_mismatch_fails_safely(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.VERIFICATION_PENDING,
        external_reference="plink_123",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("evt1"),
        event_type=RevenueEventType.PAYMENT_LINK_PAID,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "wh1"),
        merchant_id=case.merchant_id,
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        amount=Money(500, CurrencyCode.INR),
        external_reference="plink_123",
    )
    event_repo.save(event)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.VERIFICATION_PENDING


def test_currency_mismatch_fails_safely(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.VERIFICATION_PENDING,
        external_reference="plink_123",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("evt1"),
        event_type=RevenueEventType.PAYMENT_LINK_PAID,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "wh1"),
        merchant_id=case.merchant_id,
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        amount=Money(1000, CurrencyCode.USD),
        external_reference="plink_123",
    )
    event_repo.save(event)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.VERIFICATION_PENDING


def test_provider_reference_mismatch_remains_unknown(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.EXECUTION_UNKNOWN,
        idempotency_key="hash_123",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("evt1"),
        event_type=RevenueEventType.PAYMENT_LINK_PAID,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "wh1"),
        merchant_id=case.merchant_id,
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        amount=Money(1000, CurrencyCode.INR),
        metadata={
            "payload": {"payment_link": {"entity": {"reference_id": "wrong_hash"}}}
        },
    )
    event_repo.save(event)

    engine.reconcile_case(case, datetime.now(UTC))

    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.EXECUTION_UNKNOWN


def test_unpaid_created_payment_link_remains_pending(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)

    action = RecoveryAction(
        action_id=RecoveryActionId("a1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.VERIFICATION_PENDING,
        external_reference="plink_123",
        requested_at=datetime.now(UTC),
        attempt_number=1,
    )
    action_repo.save(action)

    # No event exists
    engine.reconcile_case(case, datetime.now(UTC))
    updated_action = action_repo.get(action.action_id)
    assert updated_action.status == ActionStatus.VERIFICATION_PENDING


def test_terminal_case_behavior(connection, engine, repos):
    action_repo, case_repo, event_repo, vr_repo = repos
    case = setup_case_and_merchant(connection, event_repo, case_repo)
    case.close(RecoveryOutcomeValue.EXPIRED, datetime.now(UTC))
    case_repo.save(case)

    # Reconciler should ignore closed cases
    engine.reconcile_case(case, datetime.now(UTC))
    # It just returns without error
