from datetime import UTC, datetime
from typing import Any

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.identifiers import RecoveryActionId, RecoveryCaseId
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository

from .context import MCPContext
from .registry import MCPError
from .schemas import (
    AnalyzeRootCauseInput,
    AssessRecoveryCaseInput,
    CancelPaymentLinkInput,
    CreatePaymentLinkInput,
    EscalateRecoveryCaseInput,
    GetCustomerContextInput,
    GetOrderInput,
    GetPaymentInput,
    GetPaymentLinkInput,
    GetRecoveryCaseInput,
    GetRecoveryHistoryInput,
    GetSystemHealthInput,
    RankInterventionsInput,
    ResumeRecoveryActionInput,
    SendPaymentLinkNotificationInput,
)


def handle_get_recovery_case(
    ctx: MCPContext, args: GetRecoveryCaseInput
) -> dict[str, Any]:
    with ctx.tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        case = repo.get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError(f"Case {args.case_id} not found")

        return {
            "case_id": case.case_id.value,
            "status": case.status.name,
            "workflow_state": case.workflow_state.name,
            "amount_at_risk_minor": case.amount_at_risk.amount_minor,
            "currency": case.amount_at_risk.currency.value,
        }


def handle_get_payment(ctx: MCPContext, args: GetPaymentInput) -> dict[str, Any]:
    return {
        "payment_id": args.payment_id,
        "status": "simulated_fetch",
        "is_simulated_mock": True,
    }


def handle_get_order(ctx: MCPContext, args: GetOrderInput) -> dict[str, Any]:
    return {
        "order_id": args.order_id,
        "status": "simulated_fetch",
        "is_simulated_mock": True,
    }


def handle_get_payment_link(
    ctx: MCPContext, args: GetPaymentLinkInput
) -> dict[str, Any]:
    return {
        "payment_link_id": args.payment_link_id,
        "status": "simulated_fetch",
        "is_simulated_mock": True,
    }


def handle_get_customer_context(
    ctx: MCPContext, args: GetCustomerContextInput
) -> dict[str, Any]:
    return {
        "case_id": args.case_id,
        "historical_success_rate": 0.9,
        "is_simulated_mock": True,
    }


def handle_get_recovery_history(
    ctx: MCPContext, args: GetRecoveryHistoryInput
) -> dict[str, Any]:
    # Placeholder: fetch from DB directly if repo lacks method
    with ctx.tm.transaction() as conn:
        cur = conn.execute(
            "SELECT action_id, action_type, status FROM recovery_actions WHERE case_id = ?",
            (args.case_id,),
        )
        rows = cur.fetchall()
        return {
            "case_id": args.case_id,
            "attempts": [
                {"action_id": r[0], "action_type": r[1], "status": r[2]} for r in rows
            ],
        }


def handle_get_system_health(
    ctx: MCPContext, args: GetSystemHealthInput
) -> dict[str, Any]:
    return {"systemic_degradation": False, "is_simulated_mock": True}


def handle_assess_recovery_case(
    ctx: MCPContext, args: AssessRecoveryCaseInput
) -> dict[str, Any]:
    with ctx.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        case = RecoveryCaseRepository(conn).get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError("Case not found")
        events = [
            RevenueEventRepository(conn).get(eid) for eid in case.source_event_ids
        ]

    risk, _, _ = ctx.intelligence.analyze(case, events)
    return {
        "case_id": args.case_id,
        "recovery_probability": risk.recovery_probability.value,
    }


def handle_analyze_root_cause(
    ctx: MCPContext, args: AnalyzeRootCauseInput
) -> dict[str, Any]:
    with ctx.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        case = RecoveryCaseRepository(conn).get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError("Case not found")
        events = [
            RevenueEventRepository(conn).get(eid) for eid in case.source_event_ids
        ]

    _, cause, _ = ctx.intelligence.analyze(case, events)
    return {"category": cause.category, "confidence": cause.confidence.value}


def handle_rank_interventions(
    ctx: MCPContext, args: RankInterventionsInput
) -> dict[str, Any]:
    with ctx.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        case = RecoveryCaseRepository(conn).get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError("Case not found")
        events = [
            RevenueEventRepository(conn).get(eid) for eid in case.source_event_ids
        ]

    _, _, plan = ctx.intelligence.analyze(case, events)
    candidates = []
    for cand in plan.candidates:
        candidates.append(
            {
                "candidate_id": cand.candidate_id,
                "action_type": cand.action_type.value,
                "expected_recovery_minor": cand.expected_recovery_value.amount_minor,
                "probability": cand.expected_recovery_probability.value,
            }
        )
    return {"candidates": candidates}


def handle_create_payment_link(
    ctx: MCPContext, args: CreatePaymentLinkInput
) -> dict[str, Any]:
    # 1. Fetch case
    with ctx.tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        case = case_repo.get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError(f"Case {args.case_id} not found")

        # Idempotency check:
        existing_action = action_repo.get(RecoveryActionId(args.action_id))
        if existing_action:
            return {
                "action_id": existing_action.action_id.value,
                "status": existing_action.status.name,
                "idempotent_return": True,
            }

        # Create action context
        action = RecoveryAction(
            action_id=RecoveryActionId(args.action_id),
            case_id=RecoveryCaseId(args.case_id),
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=datetime.now(UTC),
        )
        action_repo.save(action)

    with ctx.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        events = [
            RevenueEventRepository(conn).get(eid) for eid in case.source_event_ids
        ]

    # Generate real intelligence plan
    _, cause, plan = ctx.intelligence.analyze(case, events)
    import json

    action.plan_snapshot = json.dumps(plan.to_dict())
    action._real_plan = plan
    action._real_cause = cause

    # Now OUTSIDE the transaction, execute the action. ActionService will start its own transaction.
    action = ctx.action_service.execute_action(action)

    if action.status == ActionStatus.EXECUTION_UNKNOWN:
        raise MCPError("Execution status uncertain", "EXTERNAL_EXECUTION_UNCERTAINTY")
    if (
        action.status == ActionStatus.ESCALATED
        or action.status == ActionStatus.CANCELLED
    ):
        raise MCPError("Action denied by policy", "POLICY_DENIAL")

    return {
        "action_id": args.action_id,
        "provider_reference": action.external_reference,
        "status": action.status.name,
    }


def handle_send_payment_link_notification(
    ctx: MCPContext, args: SendPaymentLinkNotificationInput
) -> dict[str, Any]:
    raise MCPError(
        "Architecture does not define Razorpay notify integration", "UNSUPPORTED_TOOL"
    )


def handle_cancel_payment_link(
    ctx: MCPContext, args: CancelPaymentLinkInput
) -> dict[str, Any]:
    raise MCPError(
        "Architecture does not define Razorpay cancel integration", "UNSUPPORTED_TOOL"
    )


def handle_escalate_recovery_case(
    ctx: MCPContext, args: EscalateRecoveryCaseInput
) -> dict[str, Any]:
    with ctx.tm.transaction() as conn:
        action_repo = RecoveryActionRepository(conn)
        case_repo = RecoveryCaseRepository(conn)
        case = case_repo.get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError("Case not found")

        action = RecoveryAction(
            action_id=RecoveryActionId(f"esc_{datetime.now(UTC).timestamp()}"),
            case_id=case.case_id,
            action_type=ActionType.ESCALATE,
            status=ActionStatus.ESCALATED,
            requested_at=datetime.now(UTC),
        )
        action_repo.save(action)
        return {"case_id": args.case_id, "escalated": True, "reason": args.reason_code}


def handle_resume_recovery_action(
    ctx: MCPContext, args: ResumeRecoveryActionInput
) -> dict[str, Any]:
    with ctx.tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        case = case_repo.get(RecoveryCaseId(args.case_id))
        if not case:
            raise ValueError(f"Case {args.case_id} not found")

        action = action_repo.get(RecoveryActionId(args.action_id))
        if not action:
            raise ValueError(f"Action {args.action_id} not found")

        if action.status != ActionStatus.ESCALATED:
            raise MCPError(
                f"Action cannot be resumed from status {action.status.name}",
                "INVALID_STATE",
            )

    # Load real intelligence plan from snapshot
    if not action.plan_snapshot:
        raise MCPError("Original intervention plan snapshot not found", "MISSING_PLAN")

    import json

    from recoverai.domain.plan import InterventionPlan

    try:
        plan = InterventionPlan.from_dict(json.loads(action.plan_snapshot))
    except Exception as e:  # noqa: BLE001
        raise MCPError(
            f"Failed to load intervention plan snapshot: {e}", "CORRUPTED_PLAN"
        )
    action._real_plan = plan

    # Re-evaluate and execute through action service
    action = ctx.action_service.execute_action(action)

    if action.status == ActionStatus.EXECUTION_UNKNOWN:
        raise MCPError("Execution status uncertain", "EXTERNAL_EXECUTION_UNCERTAINTY")
    if action.status in {ActionStatus.ESCALATED, ActionStatus.CANCELLED}:
        raise MCPError("Action denied by policy upon resumption", "POLICY_DENIAL")

    return {
        "action_id": args.action_id,
        "provider_reference": action.external_reference,
        "status": action.status.name,
    }
