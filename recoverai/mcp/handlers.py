from datetime import UTC, datetime
from typing import Any

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.identifiers import RecoveryActionId, RecoveryCaseId
from recoverai.domain.policy import PolicyDecisionValue
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
    return {"payment_id": args.payment_id, "status": "simulated_fetch"}


def handle_get_order(ctx: MCPContext, args: GetOrderInput) -> dict[str, Any]:
    return {"order_id": args.order_id, "status": "simulated_fetch"}


def handle_get_payment_link(
    ctx: MCPContext, args: GetPaymentLinkInput
) -> dict[str, Any]:
    return {"payment_link_id": args.payment_link_id, "status": "simulated_fetch"}


def handle_get_customer_context(
    ctx: MCPContext, args: GetCustomerContextInput
) -> dict[str, Any]:
    return {"case_id": args.case_id, "historical_success_rate": 0.9}


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
    return {"systemic_degradation": False}


def handle_assess_recovery_case(
    ctx: MCPContext, args: AssessRecoveryCaseInput
) -> dict[str, Any]:
    return {"case_id": args.case_id, "recovery_probability": 0.8}


def handle_analyze_root_cause(
    ctx: MCPContext, args: AnalyzeRootCauseInput
) -> dict[str, Any]:
    return {"category": "CUSTOMER_ACTION", "confidence": 0.9}


def handle_rank_interventions(
    ctx: MCPContext, args: RankInterventionsInput
) -> dict[str, Any]:
    return {"candidates": []}


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

        from recoverai.domain.plan import InterventionPlan
        from recoverai.policy.engine import PolicyContext

        # 2. Authorize via Policy
        policy_context = PolicyContext(
            policy_version="1.0", current_time=datetime.now(UTC)
        )
        plan = InterventionPlan(
            plan_id=args.action_id,
            case_id=case.case_id,
            candidates=[],
            selected_action_type=None,
            selection_reason="mcp_direct_action",
            selection_model_version="manual",
            created_at=datetime.now(UTC),
        )
        decision = ctx.policy_engine.evaluate(policy_context, case, plan, [])
        if decision.decision != PolicyDecisionValue.APPROVE:
            raise MCPError("Action denied by policy", "POLICY_DENIAL")

        action.status = ActionStatus.AUTHORIZED

        # 3. Execute via Provider
        result = ctx.razorpay_service.execute_and_record(action, case, decision)

        # 4. Map result
        if "UNKNOWN" in result.result_type.name:
            raise MCPError(
                "Execution status uncertain", "EXTERNAL_EXECUTION_UNCERTAINTY"
            )

        return {
            "action_id": args.action_id,
            "provider_reference": result.provider_reference,
            "short_url": result.short_url,
            "result_type": result.result_type.name,
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
