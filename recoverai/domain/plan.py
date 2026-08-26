from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from recoverai.domain.action import ActionType
from recoverai.domain.evidence import EvidenceReference, Probability
from recoverai.domain.identifiers import RecoveryCaseId
from recoverai.domain.money import RevenueAmount


class CandidateStatus(Enum):
    PROPOSED = "PROPOSED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    INELIGIBLE = "INELIGIBLE"
    SUPPRESSED = "SUPPRESSED"


@dataclass(frozen=True)
class InterventionCandidate:
    candidate_id: str
    case_id: RecoveryCaseId
    action_type: ActionType
    expected_recovery_probability: Probability
    expected_recovery_value: RevenueAmount
    eligibility_status: CandidateStatus

    intervention_cost: RevenueAmount | None = None
    friction_score: float | None = None
    risk_score: float | None = None
    reason: str | None = None
    evidence_references: list[EvidenceReference] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.action_type, ActionType):
            raise TypeError("action_type must be an ActionType")
        if not isinstance(self.expected_recovery_probability, Probability):
            raise TypeError("expected_recovery_probability must be a Probability")
        if not isinstance(self.expected_recovery_value, RevenueAmount):
            raise TypeError("expected_recovery_value must be a RevenueAmount")
        if not isinstance(self.eligibility_status, CandidateStatus):
            raise TypeError("eligibility_status must be a CandidateStatus")
        if not self.candidate_id.strip():
            raise ValueError("candidate_id cannot be empty")


@dataclass(frozen=True)
class InterventionPlan:
    plan_id: str
    case_id: RecoveryCaseId
    candidates: list[InterventionCandidate]
    selected_action_type: ActionType | None
    selection_reason: str
    selection_model_version: str
    created_at: datetime
    expected_recovery_value: RevenueAmount | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not self.plan_id.strip():
            raise ValueError("plan_id cannot be empty")
        if not self.created_at.tzinfo:
            raise ValueError("created_at timestamp must be timezone-aware")
        if self.selected_action_type and not isinstance(
            self.selected_action_type, ActionType
        ):
            raise TypeError("selected_action_type must be an ActionType")

        # Invariants:
        for cand in self.candidates:
            if not isinstance(cand, InterventionCandidate):
                raise TypeError(
                    "candidates must contain InterventionCandidate instances"
                )

        if self.selected_action_type is not None:
            # Every selected action must have been present in the candidate set
            found = False
            for cand in self.candidates:
                if cand.action_type == self.selected_action_type:
                    found = True
                    break
            if not found:
                raise ValueError("Selected action must be present in the candidate set")
