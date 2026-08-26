from datetime import UTC, datetime

import pytest

from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType, Probability
from recoverai.domain.identifiers import (
    PolicyDecisionId,
    RecoveryActionId,
    RecoveryCaseId,
    VerificationRecordId,
)
from recoverai.domain.policy import PolicyDecision, PolicyDecisionValue
from recoverai.domain.verification import (
    VerificationRecord,
    VerificationSource,
    VerifiedState,
)


def test_probability_validation():
    p = Probability(0.75, "recovery_probability")
    assert p.value == 0.75

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        Probability(1.5, "test")

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        Probability(-0.1, "test")

    with pytest.raises(ValueError, match="meaning must be provided"):
        Probability(0.5, "")


def test_evidence_reference():
    now = datetime.now(UTC)
    ref = EvidenceReference(EvidenceSourceType.RAZORPAY_EVENT, "evt_123", now)
    assert ref.source_id == "evt_123"


def test_verification_record():
    now = datetime.now(UTC)
    record = VerificationRecord(
        verification_id=VerificationRecordId("ver_1"),
        action_id=RecoveryActionId("act_1"),
        case_id=RecoveryCaseId("case_1"),
        verification_source=VerificationSource.RAZORPAY_WEBHOOK,
        verified_state=VerifiedState.UNKNOWN,
        checked_at=now,
    )
    assert record.verified_state == VerifiedState.UNKNOWN


def test_policy_decision():
    now = datetime.now(UTC)
    decision = PolicyDecision(
        policy_decision_id=PolicyDecisionId("pol_1"),
        case_id=RecoveryCaseId("case_1"),
        action_id_or_proposal_id="act_1",
        decision=PolicyDecisionValue.APPROVE,
        policy_version="1.0.0",
        evaluated_at=now,
        reason_codes=["RISK_LOW"],
    )
    assert decision.decision == PolicyDecisionValue.APPROVE
    assert decision.reason_codes == ["RISK_LOW"]
