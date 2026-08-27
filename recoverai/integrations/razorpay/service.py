from datetime import datetime, timezone

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
        now = datetime.now(timezone.utc)

        # We must enforce domain constraints for execution boundary.
        # Ensure it has been AUTHORIZED. Usually this is checked before passing to adapter.
        if action.status == ActionStatus.AUTHORIZED:
            action.begin_execution(timestamp=now)

        # 2. Call the provider
        result = self.adapter.execute_payment_link(action, case, decision)

        # 3. Update the action with the result
        if result.provider_reference:
            action.external_reference = result.provider_reference

        now = datetime.now(timezone.utc)

        if result.result_type == RazorpayExecutionResultType.SUCCESSFUL_REQUEST:
            action.record_verification(ActionStatus.VERIFICATION_PENDING, timestamp=now)
        elif result.result_type in (
            RazorpayExecutionResultType.TIMEOUT_UNKNOWN,
            RazorpayExecutionResultType.NETWORK_UNKNOWN,
        ):
            action.failure_reason = result.error_message
            action.record_verification(ActionStatus.EXECUTION_UNKNOWN, timestamp=now)
        elif result.result_type in (
            RazorpayExecutionResultType.FAILED_BEFORE_SEND,
            RazorpayExecutionResultType.PROVIDER_REJECTED,
        ):
            action.failure_reason = result.error_message
            action.record_verification(ActionStatus.VERIFIED_FAILURE, timestamp=now)

        # 4. Persist
        self.action_repo.save(action)
        return result
