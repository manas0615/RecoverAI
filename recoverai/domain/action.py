from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from recoverai.domain.identifiers import (
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
)


class ActionType(Enum):
    WAIT = "WAIT"
    CREATE_PAYMENT_LINK = "CREATE_PAYMENT_LINK"
    SEND_PAYMENT_LINK_NOTIFICATION = "SEND_PAYMENT_LINK_NOTIFICATION"
    PAYMENT_LINK_REMINDER = "PAYMENT_LINK_REMINDER"
    ESCALATE = "ESCALATE"
    SUPPRESS = "SUPPRESS"
    # Future values can be added here (e.g. CHECKOUT_RECOVERY)


class ActionStatus(Enum):
    PROPOSED = "PROPOSED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    EXECUTION_UNKNOWN = "EXECUTION_UNKNOWN"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED_SUCCESS = "VERIFIED_SUCCESS"
    VERIFIED_FAILURE = "VERIFIED_FAILURE"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"


@dataclass
class RecoveryAction:
    """
    Represents a specific recovery execution attempt.
    Mutable lifecycle object restricted by domain methods.
    """

    action_id: RecoveryActionId
    case_id: RecoveryCaseId
    action_type: ActionType
    requested_at: datetime

    # Optional execution / policy fields
    policy_decision_id: PolicyDecisionId | None = None
    idempotency_key: str | None = None
    workflow_execution_reference: str | None = None
    external_reference: str | None = None

    # Attempt metadata
    attempt_number: int = 1

    # State fields
    status: ActionStatus = field(default=ActionStatus.PROPOSED)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failure_reason: str | None = None

    # Internal context
    _real_plan: "Any | None" = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.action_id, RecoveryActionId):
            raise TypeError("action_id must be a RecoveryActionId")
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.action_type, ActionType):
            raise TypeError("action_type must be an ActionType")
        if not self.requested_at.tzinfo:
            raise ValueError("requested_at timestamp must be timezone-aware")
        if self.attempt_number < 1:
            raise ValueError("attempt_number cannot be negative or zero")

    def authorize(self, decision_id: PolicyDecisionId, timestamp: datetime) -> None:
        if self.status != ActionStatus.PROPOSED:
            raise ValueError("Only PROPOSED actions can be authorized")
        if not isinstance(decision_id, PolicyDecisionId):
            raise TypeError("decision_id must be a PolicyDecisionId")
        if not timestamp.tzinfo:
            raise ValueError("Timestamp must be timezone-aware")

        self.policy_decision_id = decision_id
        self.status = ActionStatus.AUTHORIZED
        # A mutating financial operation must eventually get an idempotency key (by the executor),
        # but here we just record authorization.

    def begin_execution(
        self, timestamp: datetime, idempotency_key: str | None = None
    ) -> None:
        if self.status != ActionStatus.AUTHORIZED:
            raise ValueError("Only AUTHORIZED actions can begin execution")
        if not timestamp.tzinfo:
            raise ValueError("Timestamp must be timezone-aware")

        self.status = ActionStatus.EXECUTING
        self.started_at = timestamp
        if idempotency_key:
            self.idempotency_key = idempotency_key

    def record_verification(
        self, new_status: ActionStatus, timestamp: datetime
    ) -> None:
        """
        Transitions state based on verification. The full logic is in P05,
        but we enforce basic intrinsic constraints.
        """
        valid_terminal = {
            ActionStatus.VERIFIED_SUCCESS,
            ActionStatus.VERIFIED_FAILURE,
            ActionStatus.CANCELLED,
            ActionStatus.ESCALATED,
        }
        if self.status in valid_terminal:
            raise ValueError("Action is already in a terminal state")
        if (
            new_status not in valid_terminal
            and new_status != ActionStatus.VERIFICATION_PENDING
            and new_status != ActionStatus.EXECUTION_UNKNOWN
        ):
            raise ValueError("Invalid verification status transition")
        if not timestamp.tzinfo:
            raise ValueError("Timestamp must be timezone-aware")

        self.status = new_status
        if new_status in valid_terminal:
            self.completed_at = timestamp
