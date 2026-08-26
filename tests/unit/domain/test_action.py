from datetime import UTC, datetime

import pytest

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.identifiers import (
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
)


def test_recovery_action_valid_construction():
    now = datetime.now(UTC)
    action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=RecoveryCaseId("case_1"),
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
    )
    assert action.status == ActionStatus.PROPOSED


def test_recovery_action_authorization():
    now = datetime.now(UTC)
    action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=RecoveryCaseId("case_1"),
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
    )
    action.authorize(PolicyDecisionId("pol_1"), now)
    assert action.status == ActionStatus.AUTHORIZED
    assert action.policy_decision_id == PolicyDecisionId("pol_1")


def test_recovery_action_execution_and_verification():
    now = datetime.now(UTC)
    action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=RecoveryCaseId("case_1"),
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
    )

    with pytest.raises(ValueError, match="Only AUTHORIZED actions can begin execution"):
        action.begin_execution(now)

    action.authorize(PolicyDecisionId("pol_1"), now)
    action.begin_execution(now, idempotency_key="idempot_123")
    assert action.status == ActionStatus.EXECUTING
    assert action.idempotency_key == "idempot_123"

    action.record_verification(ActionStatus.VERIFIED_SUCCESS, now)
    assert action.status == ActionStatus.VERIFIED_SUCCESS
    assert action.completed_at == now

    with pytest.raises(ValueError, match="Action is already in a terminal state"):
        action.record_verification(ActionStatus.VERIFICATION_PENDING, now)
