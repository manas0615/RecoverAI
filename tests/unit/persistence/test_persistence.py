from datetime import UTC, datetime

import pytest

from recoverai.domain import (
    ActionType,
    CurrencyCode,
    CustomerId,
    EventSource,
    EventSourceType,
    MerchantId,
    Money,
    PolicyDecisionId,
    RecoveryAction,
    RecoveryActionId,
    RecoveryCase,
    RecoveryCaseId,
    RecoveryCaseStatus,
    RecoveryOutcomeValue,
    RevenueAmount,
    RevenueEvent,
    RevenueEventId,
    RevenueEventType,
    RevenueSource,
)
from recoverai.persistence.exceptions import DuplicateEntityError
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository


def test_money_roundtrip(tm):
    now = datetime.now(UTC)
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "ext_1"),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
        amount=Money(5000, CurrencyCode.INR),
    )

    with tm.transaction() as conn:
        repo = RevenueEventRepository(conn)
        repo.save(ev)

    with tm.transaction() as conn:
        repo = RevenueEventRepository(conn)
        loaded = repo.get(RevenueEventId("evt_1"))

    assert loaded is not None
    assert loaded.amount is not None
    assert loaded.amount.amount_minor == 5000
    assert loaded.amount.currency == CurrencyCode.INR


def test_transaction_rollback(tm):
    now = datetime.now(UTC)
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_2"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "ext_2"),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
        amount=Money(5000, CurrencyCode.INR),
    )

    try:
        with tm.transaction() as conn:
            repo = RevenueEventRepository(conn)
            repo.save(ev)
            # Intentionally cause a failure
            raise RuntimeError("Force rollback")
    except RuntimeError:
        pass

    # Verify it was rolled back
    with tm.transaction() as conn:
        repo = RevenueEventRepository(conn)
        loaded = repo.get(RevenueEventId("evt_2"))
        assert loaded is None


def test_unique_constraint_source_event(tm):
    now = datetime.now(UTC)
    ev1 = RevenueEvent(
        event_id=RevenueEventId("evt_3"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "ext_shared"),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )
    ev2 = RevenueEvent(
        event_id=RevenueEventId("evt_4"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "ext_shared"),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )

    with tm.transaction() as conn:
        repo = RevenueEventRepository(conn)
        repo.save(ev1)

        with pytest.raises(DuplicateEntityError, match="UNIQUE constraint failed"):
            repo.save(ev2)


def test_recovery_case_lifecycle_roundtrip(tm):
    now = datetime.now(UTC)

    # First persist an event
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_case"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.INTERNAL),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )
    with tm.transaction() as conn:
        RevenueEventRepository(conn).save(ev)

    case = RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m_1"),
        customer_id=CustomerId("c_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_case")},
    )

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        repo.save(case)

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        loaded = repo.get(RecoveryCaseId("case_1"))

    assert loaded is not None
    assert loaded.status == RecoveryCaseStatus.OPEN
    assert RevenueEventId("evt_case") in loaded.source_event_ids

    # Update state
    loaded.close(
        RecoveryOutcomeValue.RECOVERED,
        now,
        RevenueAmount(Money(1000, CurrencyCode.INR)),
    )
    with tm.transaction() as conn:
        RecoveryCaseRepository(conn).save(loaded)

    with tm.transaction() as conn:
        closed = RecoveryCaseRepository(conn).get(RecoveryCaseId("case_1"))

    assert closed.status == RecoveryCaseStatus.CLOSED
    assert closed.outcome_type == RecoveryOutcomeValue.RECOVERED


def test_idempotency_concurrency_protection(tm):
    now = datetime.now(UTC)

    # Case must exist to satisfy FK
    case = RecoveryCase(
        case_id=RecoveryCaseId("case_idx"),
        merchant_id=MerchantId("m_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={
            RevenueEventId("evt_case_fake")
        },  # Ignored for FK check since case_source_events FK is event_id, wait, case_source_events checks revenue_events. We'll disable FK or just insert event.
    )
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_case_fake"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.INTERNAL),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )
    with tm.transaction() as conn:
        RevenueEventRepository(conn).save(ev)
        RecoveryCaseRepository(conn).save(case)
        # Satisfy PolicyDecision FK
        conn.execute("""
            INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
            VALUES ('pol_1', 'case_idx', 'act_1', 'APPROVE', '1.0', '[]', '[]', '2026-01-01T00:00:00+00:00')
        """)
        conn.execute("""
            INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
            VALUES ('pol_2', 'case_idx', 'act_2', 'APPROVE', '1.0', '[]', '[]', '2026-01-01T00:00:00+00:00')
        """)

    # Create action with idempotency key
    action1 = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=RecoveryCaseId("case_idx"),
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
    )
    action1.authorize(PolicyDecisionId("pol_1"), now)
    action1.begin_execution(now, idempotency_key="idemp_1")

    # Create competing action with same idempotency key
    action2 = RecoveryAction(
        action_id=RecoveryActionId("act_2"),
        case_id=RecoveryCaseId("case_idx"),
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
    )
    action2.authorize(PolicyDecisionId("pol_2"), now)
    action2.begin_execution(now, idempotency_key="idemp_1")

    with tm.transaction() as conn:
        repo = RecoveryActionRepository(conn)
        repo.save(action1)

        with pytest.raises(DuplicateEntityError, match="UNIQUE constraint failed"):
            repo.save(action2)
