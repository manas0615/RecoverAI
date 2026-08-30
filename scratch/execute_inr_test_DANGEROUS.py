import os
import sys
from datetime import UTC, datetime
from uuid import uuid4

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from recoverai.api.main import container
from recoverai.domain.action import (
    ActionStatus,
    ActionType,
    RecoveryAction,
    RecoveryActionId,
)
from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCase,
    RecoveryCaseId,
    RevenueSource,
)
from recoverai.domain.identifiers import CustomerId, MerchantId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer


def run_inr_test():
    case_id = RecoveryCaseId("case_INR_9")

    # Check if exists
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.case import RecoveryCaseRepository

        repo = RecoveryCaseRepository(conn)
        existing = repo.get(case_id)

    if existing:
        print("Case already exists!")
        return

    # Create case
    case = RecoveryCase(
        case_id=case_id,
        merchant_id=MerchantId("merch_demo"),
        customer_id=CustomerId("cust_demo"),
        revenue_source=RevenueSource.SUBSCRIPTION,
        amount_at_risk=RevenueAmount(Money(50000, CurrencyCode.INR)),  # 500 INR
        opened_at=datetime.now(UTC),
        workflow_state=CaseWorkflowState.DETECTED,
        source_event_ids=[RevenueEventId("evt_LIVE")],
        version=0,
    )

    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.case import RecoveryCaseRepository

        repo = RecoveryCaseRepository(conn)
        repo.save(case)

    print("Created case_INR")

    # Analyze
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        repo = RevenueEventRepository(conn)
        evt = repo.get(RevenueEventId("evt_LIVE"))
        events = [evt] if evt else []
        analyzer = RevenueIntelligenceAnalyzer(container.llm)
        _, _, plan = analyzer.analyze(case, events)
    print("Plan:", plan)

    # Propose Action
    action_id = f"act_{uuid4().hex[:12]}"
    action = RecoveryAction(
        action_id=RecoveryActionId(action_id),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        status=ActionStatus.PROPOSED,
        requested_at=datetime.now(UTC),
        idempotency_key=action_id,
    )
    action._real_plan = plan

    # Policy
    from recoverai.policy.engine import PolicyContext

    ctx = PolicyContext(
        policy_version="1.0",
        current_time=datetime.now(UTC),
    )
    decision = container.policy.evaluate(ctx, case, plan, [])
    print("Decision:", decision.decision)

    if decision.decision.name != "APPROVE":
        print("Not approved, stopping.")
        return

    action.status = ActionStatus.AUTHORIZED

    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.action import RecoveryActionRepository

        repo = RecoveryActionRepository(conn)
        repo.save(action)

    print("Executing Action...")
    result_action = container.action_service.execute_action(action)
    print(f"Action Status: {result_action.status}")
    print(f"External Ref: {result_action.external_reference}")


if __name__ == "__main__":
    run_inr_test()
