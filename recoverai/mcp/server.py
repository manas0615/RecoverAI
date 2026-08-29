from .context import MCPContext
from .handlers import (
    handle_analyze_root_cause,
    handle_assess_recovery_case,
    handle_cancel_payment_link,
    handle_create_payment_link,
    handle_escalate_recovery_case,
    handle_get_customer_context,
    handle_get_order,
    handle_get_payment,
    handle_get_payment_link,
    handle_get_recovery_case,
    handle_get_recovery_history,
    handle_get_system_health,
    handle_rank_interventions,
    handle_send_payment_link_notification,
)
from .registry import MCPToolRegistry
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


def create_mcp_registry(ctx: MCPContext) -> MCPToolRegistry:
    registry = MCPToolRegistry(ctx)

    # READ
    registry.register(
        "get_recovery_case",
        "READ",
        "LOW",
        GetRecoveryCaseInput,
        handle_get_recovery_case,
    )
    registry.register("get_payment", "READ", "LOW", GetPaymentInput, handle_get_payment)
    registry.register("get_order", "READ", "LOW", GetOrderInput, handle_get_order)
    registry.register(
        "get_payment_link", "READ", "LOW", GetPaymentLinkInput, handle_get_payment_link
    )
    registry.register(
        "get_customer_context",
        "READ",
        "LOW",
        GetCustomerContextInput,
        handle_get_customer_context,
    )
    registry.register(
        "get_recovery_history",
        "READ",
        "LOW",
        GetRecoveryHistoryInput,
        handle_get_recovery_history,
    )
    registry.register(
        "get_system_health",
        "READ",
        "LOW",
        GetSystemHealthInput,
        handle_get_system_health,
    )

    # ANALYZE
    registry.register(
        "assess_recovery_case",
        "ANALYZE",
        "LOW",
        AssessRecoveryCaseInput,
        handle_assess_recovery_case,
    )
    registry.register(
        "analyze_root_cause",
        "ANALYZE",
        "LOW",
        AnalyzeRootCauseInput,
        handle_analyze_root_cause,
    )
    registry.register(
        "rank_interventions",
        "ANALYZE",
        "LOW",
        RankInterventionsInput,
        handle_rank_interventions,
    )

    # ACT
    registry.register(
        "create_payment_link",
        "ACT",
        "HIGH",
        CreatePaymentLinkInput,
        handle_create_payment_link,
        requires_policy=True,
        requires_verification=True,
        idempotency_required=True,
    )
    registry.register(
        "send_payment_link_notification",
        "ACT",
        "MEDIUM",
        SendPaymentLinkNotificationInput,
        handle_send_payment_link_notification,
        requires_policy=True,
    )
    registry.register(
        "cancel_payment_link",
        "ACT",
        "HIGH",
        CancelPaymentLinkInput,
        handle_cancel_payment_link,
        requires_policy=True,
        requires_verification=True,
    )
    registry.register(
        "escalate_recovery_case",
        "ACT",
        "MEDIUM",
        EscalateRecoveryCaseInput,
        handle_escalate_recovery_case,
        requires_policy=True,
    )

    from .handlers import handle_resume_recovery_action
    from .schemas import ResumeRecoveryActionInput

    registry.register(
        "resume_recovery_action",
        "ACT",
        "HIGH",
        ResumeRecoveryActionInput,
        handle_resume_recovery_action,
        requires_policy=True,
        requires_verification=True,
        idempotency_required=True,
    )

    return registry
