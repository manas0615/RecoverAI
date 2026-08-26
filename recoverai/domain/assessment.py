from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from recoverai.domain.evidence import EvidenceReference, Probability
from recoverai.domain.identifiers import RecoveryCaseId
from recoverai.domain.money import RevenueAmount


class AnalysisType(Enum):
    RULE_BASED = "RULE_BASED"
    STATISTICAL = "STATISTICAL"
    ML = "ML"
    LLM = "LLM"
    HYBRID = "HYBRID"


@dataclass(frozen=True)
class RiskAssessment:
    assessment_id: str
    case_id: RecoveryCaseId
    recovery_probability: Probability
    expected_recovery_value: RevenueAmount
    model_name: str
    model_version: str
    created_at: datetime
    feature_snapshot_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.recovery_probability, Probability):
            raise TypeError("recovery_probability must be a Probability")
        if not isinstance(self.expected_recovery_value, RevenueAmount):
            raise TypeError("expected_recovery_value must be a RevenueAmount")
        if not self.assessment_id.strip():
            raise ValueError("assessment_id cannot be empty")
        if not self.created_at.tzinfo:
            raise ValueError("created_at timestamp must be timezone-aware")


@dataclass(frozen=True)
class CauseAssessment:
    cause_assessment_id: str
    case_id: RecoveryCaseId
    category: str
    confidence: Probability
    analysis_type: AnalysisType
    model_version: str
    created_at: datetime
    evidence_references: list[EvidenceReference] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.confidence, Probability):
            raise TypeError("confidence must be a Probability")
        if not isinstance(self.analysis_type, AnalysisType):
            raise TypeError("analysis_type must be an AnalysisType")
        if not self.cause_assessment_id.strip():
            raise ValueError("cause_assessment_id cannot be empty")
        if not self.created_at.tzinfo:
            raise ValueError("created_at timestamp must be timezone-aware")
        for ev in self.evidence_references:
            if not isinstance(ev, EvidenceReference):
                raise TypeError(
                    "evidence_references must contain only EvidenceReference instances"
                )
