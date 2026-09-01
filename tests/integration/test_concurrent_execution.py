import json
import sqlite3
import threading
import time
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from recoverai.api.main import container
from recoverai.domain import (
    CustomerId,
    MerchantId,
    RecoveryActionId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCase,
    RecoveryCaseStatus,
    RevenueSource,
)
from recoverai.domain.event import (
    EventSource,
    EventSourceType,
    RevenueEvent,
    RevenueEventType,
)
from recoverai.domain.evidence import Probability
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.domain.plan import (
    CandidateStatus,
    InterventionCandidate,
    InterventionPlan,
)
from recoverai.integrations.razorpay.adapter import (
    RazorpayExecutionResult,
    RazorpayExecutionResultType,
)
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository


def test_concurrent_execution():
    tm = container.tm
    case_id = RecoveryCaseId(f"case_{uuid.uuid4().hex[:12]}")
    action_id = RecoveryActionId(f"act_{uuid.uuid4().hex[:12]}")
    event_id = RevenueEventId(f"ev_{uuid.uuid4().hex[:12]}")

    with tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_demo', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO customers (customer_id, merchant_id, display_name, created_at, updated_at) VALUES ('cust_demo', 'merch_demo', 'Demo Customer', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )

        event_repo = RevenueEventRepository(conn)
        event = RevenueEvent(
            event_id=event_id,
            merchant_id=MerchantId("merch_demo"),
            customer_id=CustomerId("cust_demo"),
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(
                source_type=EventSourceType.RAZORPAY_WEBHOOK,
                source_event_id=f"test_{uuid.uuid4().hex}",
            ),
            amount=Money(1000, CurrencyCode.INR),
            occurred_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
            metadata={},
        )
        event_repo.save(event)

        case_repo = RecoveryCaseRepository(conn)
        case = RecoveryCase(
            case_id=case_id,
            merchant_id=MerchantId("merch_demo"),
            customer_id=CustomerId("cust_demo"),
            revenue_source=RevenueSource.SUBSCRIPTION,
            amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.INR)),
            status=RecoveryCaseStatus.OPEN,
            workflow_state=CaseWorkflowState.WAITING_APPROVAL,
            source_event_ids=[event_id],
            opened_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        case_repo.save(case)

        action_repo = RecoveryActionRepository(conn)
        candidate = InterventionCandidate(
            candidate_id=f"cand_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            expected_recovery_probability=Probability(0.9, meaning="test"),
            expected_recovery_value=RevenueAmount(Money(1000, CurrencyCode.INR)),
            eligibility_status=CandidateStatus.SELECTED,
        )
        plan = InterventionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            candidates=[candidate],
            selected_action_type=ActionType.CREATE_PAYMENT_LINK,
            selection_reason="Test",
            selection_model_version="test",
            created_at=datetime.now(UTC),
            expected_recovery_value=RevenueAmount(Money(1000, CurrencyCode.INR)),
        )

        action = RecoveryAction(
            action_id=action_id,
            case_id=case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.ESCALATED,
            requested_at=datetime.now(UTC),
        )
        action.plan_snapshot = json.dumps(plan.to_dict())
        action_repo.save(action)

    mock_execute = MagicMock()

    def slow_execute(*args, **kwargs):
        time.sleep(1.0)
        return RazorpayExecutionResult(
            result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
            provider_reference=f"plink_{uuid.uuid4().hex[:8]}",
        )

    mock_execute.side_effect = slow_execute
    original_adapter = container.action_service.razorpay_adapter
    container.action_service.razorpay_adapter = MagicMock()
    container.action_service.razorpay_adapter.execute_payment_link = mock_execute

    barrier = threading.Barrier(2)

    def worker():
        with tm.transaction() as conn:
            action_repo = RecoveryActionRepository(conn)
            action = action_repo.get(action_id)

            action._real_plan = InterventionPlan.from_dict(
                json.loads(action.plan_snapshot)
            )
            cause_mock = MagicMock()
            cause_mock.category.name = "PAYMENT_FAILED"
            action._real_cause = cause_mock

        barrier.wait()
        try:
            container.action_service.execute_action(action)
        except sqlite3.OperationalError:
            pass  # Expected when database gets locked by concurrent claim
        except RuntimeError as e:
            if "Concurrency violation" not in str(e):
                raise
        except Exception as e:
            print("Worker exception:", type(e).__name__, e)

    threads = []
    for i in range(2):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Restore
    container.action_service.razorpay_adapter = original_adapter

    assert mock_execute.call_count == 1, (
        f"Concurrency race detected! Provider called {mock_execute.call_count} times."
    )
