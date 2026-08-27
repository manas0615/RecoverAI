from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.assessment import CauseAssessment
from recoverai.domain.case import RecoveryCase, RecoveryCaseStatus
from recoverai.domain.identifiers import PolicyDecisionId
from recoverai.domain.money import RevenueAmount
from recoverai.domain.plan import InterventionPlan
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue


@dataclass(frozen=True)
class PolicyContext:
    """
    Immutable configuration for a single policy evaluation.
    Distinguishes merchant-configured rules from system safety invariants.
    """

    policy_version: str
    current_time: datetime
    # Merchant-configurable policies
    max_attempts_per_case: int = 3
    high_value_threshold: RevenueAmount | None = None


class PolicyEngine:
    """
    Deterministic Policy Engine acting as a safety boundary.
    Evaluates InterventionPlans against domain facts and returns a PolicyDecision.
    """

    def __init__(self, generate_decision_id: Callable[[], str]):
        self.generate_decision_id = generate_decision_id

    def evaluate(
        self,
        context: PolicyContext,
        case: RecoveryCase,
        plan: InterventionPlan,
        action_history: list[RecoveryAction],
        cause: CauseAssessment | None = None,
    ) -> PolicyDecision:
        """
        Evaluates the proposed action in the plan against policy rules.
        """
        proposed_action_type = plan.selected_action_type

        # Fail-closed: missing proposed action
        if proposed_action_type is None:
            return self._build_decision(
                context, case, plan, PolicyDecisionValue.DENY, "MISSING_PROPOSED_ACTION"
            )

        # ---------------------------------------------------------------------
        # 1. HARD SYSTEM SAFETY INVARIANTS
        # ---------------------------------------------------------------------

        # 1.1 Terminal Case Protection
        if case.status == RecoveryCaseStatus.CLOSED:
            return self._build_decision(
                context, case, plan, PolicyDecisionValue.DENY, "CASE_TERMINAL"
            )

        # 1.2 Current External-State Validity
        unknown_actions = [
            a for a in action_history if a.status == ActionStatus.EXECUTION_UNKNOWN
        ]
        if any(a.action_type == proposed_action_type for a in unknown_actions):
            return self._build_decision(
                context,
                case,
                plan,
                PolicyDecisionValue.DENY,
                "UNCERTAIN_EXTERNAL_STATE",
            )

        # 1.3 Duplicate-Action Protection
        active_statuses = {
            ActionStatus.PROPOSED,
            ActionStatus.AUTHORIZED,
            ActionStatus.EXECUTING,
            ActionStatus.VERIFICATION_PENDING,
        }
        active_actions = [a for a in action_history if a.status in active_statuses]
        if any(a.action_type == proposed_action_type for a in active_actions):
            return self._build_decision(
                context,
                case,
                plan,
                PolicyDecisionValue.DENY,
                "DUPLICATE_ACTIVE_RECOVERY_ACTION",
            )

        # 1.4 Action Eligibility (Allowed Actions)
        allowed_actions = {
            ActionType.WAIT,
            ActionType.CREATE_PAYMENT_LINK,
            ActionType.SEND_PAYMENT_LINK_NOTIFICATION,
            ActionType.PAYMENT_LINK_REMINDER,
            ActionType.SUPPRESS,
            ActionType.ESCALATE,
        }
        if proposed_action_type not in allowed_actions:
            return self._build_decision(
                context, case, plan, PolicyDecisionValue.DENY, "ACTION_NOT_ELIGIBLE"
            )

        # ---------------------------------------------------------------------
        # 2. SYSTEMIC DEGRADATION (Contextual Safety Rule)
        # ---------------------------------------------------------------------
        if (
            cause
            and cause.category == "SYSTEMIC_DEGRADATION"
            and proposed_action_type
            not in {
                ActionType.WAIT,
                ActionType.SUPPRESS,
                ActionType.ESCALATE,
            }
        ):
            return self._build_decision(
                context,
                case,
                plan,
                PolicyDecisionValue.SUPPRESS,
                "SYSTEMIC_DEGRADATION",
            )

        # ---------------------------------------------------------------------
        # 3. MERCHANT CONFIGURABLE POLICY
        # ---------------------------------------------------------------------

        # 3.1 Attempt Limits
        mutating_actions = {
            ActionType.CREATE_PAYMENT_LINK,
            ActionType.SEND_PAYMENT_LINK_NOTIFICATION,
            ActionType.PAYMENT_LINK_REMINDER,
        }
        if proposed_action_type in mutating_actions:
            mutating_attempts = [
                a for a in action_history if a.action_type in mutating_actions
            ]
            if len(mutating_attempts) >= context.max_attempts_per_case:
                return self._build_decision(
                    context,
                    case,
                    plan,
                    PolicyDecisionValue.SUPPRESS,
                    "ATTEMPT_LIMIT_REACHED",
                )

        # 3.2 High-Value Approval
        if context.high_value_threshold is not None:
            if case.amount_at_risk.currency != context.high_value_threshold.currency:
                return self._build_decision(
                    context,
                    case,
                    plan,
                    PolicyDecisionValue.ESCALATE,
                    "CURRENCY_MISMATCH_IN_POLICY",
                )
            if (
                case.amount_at_risk.amount_minor
                > context.high_value_threshold.amount_minor
            ) and proposed_action_type not in {
                ActionType.ESCALATE,
                ActionType.WAIT,
                ActionType.SUPPRESS,
            }:
                return self._build_decision(
                    context,
                    case,
                    plan,
                    PolicyDecisionValue.ESCALATE,
                    "HIGH_VALUE_ACTION",
                )

        # ---------------------------------------------------------------------
        # 4. DEFAULT APPROVAL
        # ---------------------------------------------------------------------
        return self._build_decision(
            context, case, plan, PolicyDecisionValue.APPROVE, "POLICY_APPROVED"
        )

    def _build_decision(
        self,
        context: PolicyContext,
        case: RecoveryCase,
        plan: InterventionPlan,
        decision_value: PolicyDecisionValue,
        reason_code: str,
    ) -> PolicyDecision:
        return PolicyDecision(
            policy_decision_id=PolicyDecisionId(self.generate_decision_id()),
            case_id=case.case_id,
            action_id_or_proposal_id=plan.plan_id,
            decision=decision_value,
            policy_version=context.policy_version,
            evaluated_at=context.current_time,
            matched_rules=[reason_code],
            reason_codes=[reason_code],
        )
