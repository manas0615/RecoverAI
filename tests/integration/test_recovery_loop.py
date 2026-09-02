import uuid
import pytest
from datetime import UTC, datetime
from recoverai.domain.event import RevenueEvent, RevenueEventType, EventSource, EventSourceType
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId, RecoveryActionId, RevenueEventId
from recoverai.domain.money import Money, CurrencyCode, RevenueAmount
from recoverai.domain.case import RecoveryCase, RevenueSource, CaseWorkflowState
from recoverai.domain.action import RecoveryAction, ActionType, ActionStatus
from recoverai.application.case_manager import RecoveryCaseManager
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.event import RevenueEventRepository

@pytest.fixture
def tm():
    return TransactionManager()

@pytest.fixture
def cm(tm):
    return RecoveryCaseManager(tm)

def ensure_merchant(tm, merch_id="merch_demo"):
    with tm.transaction() as conn:
        conn.execute("INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES (?, 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')", (merch_id,))

def test_recovery_payment_failure_loop(tm, cm):
    ensure_merchant(tm)
    merchant_id = MerchantId("merch_demo")
    case_id = RecoveryCaseId("case_orig123")
    act_id = RecoveryActionId("act_orig456")
    plink_id = "plink_TXJTUCvi8TqV88"
    ev_id = RevenueEventId("ev_orig123")
    
    with tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        event_repo = RevenueEventRepository(conn)
        
        orig_ev = RevenueEvent(event_id=ev_id, event_type=RevenueEventType.PAYMENT_FAILED, source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_1"), merchant_id=merchant_id, amount=Money(75000, CurrencyCode.INR), occurred_at=datetime.now(UTC), received_at=datetime.now(UTC), metadata={})
        event_repo.save(orig_ev)

        orig_case = RecoveryCase(
            case_id=case_id,
            merchant_id=merchant_id,
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(75000, CurrencyCode.INR)),
            opened_at=datetime.now(UTC),
            source_event_ids={ev_id}
        )
        orig_case.workflow_state = CaseWorkflowState.VERIFYING
        case_repo.save(orig_case)
        
        action = RecoveryAction(
            action_id=act_id,
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.VERIFICATION_PENDING,
            requested_at=datetime.now(UTC),
            external_reference=plink_id,
        )
        action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("ev_new_failure"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_fail123"),
        merchant_id=merchant_id,
        amount=Money(75000, CurrencyCode.INR),
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        metadata={"payload": {"payment": {"entity": {"description": f"#{plink_id.replace('plink_', '')}"}}}}
    )
    
    with tm.transaction() as conn: RevenueEventRepository(conn).save(event)
    result_case = cm.create_or_update_from_event(event)
    
    with tm.transaction() as conn:
        assert result_case is not None
        assert result_case.case_id == case_id
        action_repo = RecoveryActionRepository(conn)
        updated_action = action_repo.get(act_id)
        assert updated_action.status == ActionStatus.VERIFIED_FAILURE
        case_repo = RecoveryCaseRepository(conn)
        updated_case = case_repo.get(case_id)
        assert updated_case.workflow_state == CaseWorkflowState.PLANNING

def test_primary_payment_failure(tm, cm):
    ensure_merchant(tm)
    merchant_id = MerchantId("merch_demo")
    
    event = RevenueEvent(
        event_id=RevenueEventId("ev_primary_fail"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_primary123"),
        merchant_id=merchant_id,
        amount=Money(10000, CurrencyCode.INR),
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        metadata={"payload": {"payment": {"entity": {"description": "Standard Order Description"}}}}
    )
    
    with tm.transaction() as conn: RevenueEventRepository(conn).save(event)
    result_case = cm.create_or_update_from_event(event)
    assert result_case is not None
    assert result_case.case_id.value == "case_wh_primary123"

def test_recovery_payment_failure_idempotent(tm, cm):
    ensure_merchant(tm)
    merchant_id = MerchantId("merch_demo")
    case_id = RecoveryCaseId("case_idem_test")
    act_id = RecoveryActionId("act_idem_test")
    plink_id = "plink_IDEM123"
    ev_id = RevenueEventId("ev_idem_orig")
    
    with tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        event_repo = RevenueEventRepository(conn)
        
        orig_ev = RevenueEvent(event_id=ev_id, event_type=RevenueEventType.PAYMENT_FAILED, source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_2"), merchant_id=merchant_id, amount=Money(75000, CurrencyCode.INR), occurred_at=datetime.now(UTC), received_at=datetime.now(UTC), metadata={})
        event_repo.save(orig_ev)
        
        orig_case = RecoveryCase(
            case_id=case_id,
            merchant_id=merchant_id,
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(75000, CurrencyCode.INR)),
            opened_at=datetime.now(UTC),
            source_event_ids={ev_id}
        )
        case_repo.save(orig_case)
        
        action = RecoveryAction(
            action_id=act_id,
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.VERIFICATION_PENDING,
            requested_at=datetime.now(UTC),
            external_reference=plink_id,
        )
        action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("ev_fail_idem"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_idem123"),
        merchant_id=merchant_id,
        amount=Money(75000, CurrencyCode.INR),
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        metadata={"payload": {"payment": {"entity": {"description": f"#{plink_id.replace('plink_', '')}"}}}}
    )
    
    with tm.transaction() as conn: RevenueEventRepository(conn).save(event)
    res1 = cm.create_or_update_from_event(event)
    assert res1.case_id == case_id
    
    with tm.transaction() as conn:
        conn.execute("INSERT INTO case_source_events (case_id, event_id) VALUES (?, ?)", (res1.case_id.value, event.event_id.value))
        
    res2 = cm.create_or_update_from_event(event)
    assert res2.case_id == case_id

def test_cross_case_safety(tm, cm):
    ensure_merchant(tm)
    merchant_id = MerchantId("merch_demo")
    case_id = RecoveryCaseId("case_unrelated")
    act_id = RecoveryActionId("act_unrelated")
    plink_id = "plink_UNRELATED"
    ev_id = RevenueEventId("ev_unrel")
    
    with tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        event_repo = RevenueEventRepository(conn)
        
        orig_ev = RevenueEvent(event_id=ev_id, event_type=RevenueEventType.PAYMENT_FAILED, source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_3"), merchant_id=merchant_id, amount=Money(75000, CurrencyCode.INR), occurred_at=datetime.now(UTC), received_at=datetime.now(UTC), metadata={})
        event_repo.save(orig_ev)
        
        orig_case = RecoveryCase(
            case_id=case_id,
            merchant_id=merchant_id,
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(75000, CurrencyCode.INR)),
            opened_at=datetime.now(UTC),
            source_event_ids={ev_id}
        )
        case_repo.save(orig_case)
        
        action = RecoveryAction(
            action_id=act_id,
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.VERIFICATION_PENDING,
            requested_at=datetime.now(UTC),
            external_reference=plink_id,
        )
        action_repo.save(action)

    event = RevenueEvent(
        event_id=RevenueEventId("ev_fail_other"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh_other123"),
        merchant_id=merchant_id,
        amount=Money(75000, CurrencyCode.INR),
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        metadata={"payload": {"payment": {"entity": {"description": "#DIFFERENTLINK"}}}}
    )
    
    with tm.transaction() as conn: RevenueEventRepository(conn).save(event)
    res = cm.create_or_update_from_event(event)
    assert res.case_id != RecoveryCaseId("case_unrelated")
    
    with tm.transaction() as conn:
        action = RecoveryActionRepository(conn).get(RecoveryActionId("act_unrelated"))
        assert action.status == ActionStatus.VERIFICATION_PENDING
