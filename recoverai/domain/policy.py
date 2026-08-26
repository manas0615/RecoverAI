from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from recoverai.domain.identifiers import PolicyDecisionId, RecoveryCaseId


class PolicyDecisionValue(Enum):
    APPROVE = "APPROVE"
    DENY = "DENY"
    SUPPRESS = "SUPPRESS"
    ESCALATE = "ESCALATE"
    REVALIDATE = "REVALIDATE"


@dataclass(frozen=True)
class PolicyDecision:
    """
    Immutable record of a deterministic authorization/rejection logic.
    Does NOT execute policy, just records it.
    """

    policy_decision_id: PolicyDecisionId
    case_id: RecoveryCaseId
    action_id_or_proposal_id: str
    decision: PolicyDecisionValue
    policy_version: str
    evaluated_at: datetime

    matched_rules: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.policy_decision_id, PolicyDecisionId):
            raise TypeError("policy_decision_id must be a PolicyDecisionId")
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.decision, PolicyDecisionValue):
            raise TypeError("decision must be a PolicyDecisionValue")
        if not self.action_id_or_proposal_id.strip():
            raise ValueError("action_id_or_proposal_id cannot be empty")
        if not self.policy_version.strip():
            raise ValueError("policy_version cannot be empty")
        if not self.evaluated_at.tzinfo:
            raise ValueError("evaluated_at timestamp must be timezone-aware")
