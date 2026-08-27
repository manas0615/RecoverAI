from datetime import UTC, datetime

from recoverai.domain.action import ActionStatus, RecoveryAction
from recoverai.domain.case import RecoveryCase
from recoverai.domain.policy import PolicyDecision
from recoverai.integrations.razorpay.adapter import (
    RazorpayAdapter,
    RazorpayExecutionResult,
    RazorpayExecutionResultType,
)
from recoverai.persistence.repositories.action import RecoveryActionRepository


class RazorpayExecutionService:
    def __init__(
        self, adapter: RazorpayAdapter, action_repo: RecoveryActionRepository
    ) -> None:
        self.adapter = adapter
        self.action_repo = action_repo

    def execute_and_record(
        self, action: RecoveryAction, case: RecoveryCase, decision: PolicyDecision
    ) -> RazorpayExecutionResult:
        # 1. Update action status to EXECUTING before calling network (if architecture specifies)
        # Actually P05 manages workflow transitions, but action status is tracked here.
        if (
            action.status
            not in (ActionStatus.VERIFICATION_PENDING, ActionStatus.EXECUTION_UNKNOWN)
            and action.status == ActionStatus.VERIFIED_SUCCESS
        ):
            return RazorpayExecutionResult(
                result_type=RazorpayExecutionResultType.FAILED_BEFORE_SEND,
                error_message="Action already verified success",
            )

        # 2. Call the provider
        result = self.adapter.execute_payment_link(action, case, decision)

        # 3. Update the action with the result
        if result.provider_reference:
            action.external_reference = result.provider_reference

        now = datetime.now(UTC)
        if not action.started_at:
            action.started_at = now

        if result.result_type == RazorpayExecutionResultType.SUCCESSFUL_REQUEST:
            action.status = ActionStatus.VERIFICATION_PENDING
        elif result.result_type in (
            RazorpayExecutionResultType.TIMEOUT_UNKNOWN,
            RazorpayExecutionResultType.NETWORK_UNKNOWN,
        ):
            action.status = ActionStatus.EXECUTION_UNKNOWN
            action.failure_reason = result.error_message
        elif result.result_type in (
            RazorpayExecutionResultType.FAILED_BEFORE_SEND,
            RazorpayExecutionResultType.PROVIDER_REJECTED,
        ):
            action.status = ActionStatus.VERIFIED_FAILURE
            action.completed_at = now
            action.failure_reason = result.error_message

        # 4. Persist
        self.action_repo.save(action)
        return result
