from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from recoverai.domain.evidence import EvidenceReference
from recoverai.domain.identifiers import (
    RecoveryActionId,
    RecoveryCaseId,
    VerificationRecordId,
)


class VerifiedState(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"


class VerificationSource(Enum):
    RAZORPAY_WEBHOOK = "RAZORPAY_WEBHOOK"
    RAZORPAY_API = "RAZORPAY_API"
    PAYMENT_LINK_WEBHOOK = "PAYMENT_LINK_WEBHOOK"
    SIMULATOR = "SIMULATOR"
    MANUAL_REVIEW = "MANUAL_REVIEW"


@dataclass(frozen=True)
class VerificationRecord:
    """
    Records how RecoverAI determined the final business state after execution.
    UNKNOWN is a first-class domain state, distinct from FAILURE.
    """

    verification_id: VerificationRecordId
    action_id: RecoveryActionId
    case_id: RecoveryCaseId
    verification_source: VerificationSource
    verified_state: VerifiedState
    checked_at: datetime

    external_reference: str | None = None
    evidence_reference: EvidenceReference | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.verification_id, VerificationRecordId):
            raise TypeError("verification_id must be a VerificationRecordId")
        if not isinstance(self.action_id, RecoveryActionId):
            raise TypeError("action_id must be a RecoveryActionId")
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.verification_source, VerificationSource):
            raise TypeError("verification_source must be a VerificationSource")
        if not isinstance(self.verified_state, VerifiedState):
            raise TypeError("verified_state must be a VerifiedState")
        if not self.checked_at.tzinfo:
            raise ValueError("checked_at timestamp must be timezone-aware")
