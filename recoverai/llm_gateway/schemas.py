import math

from pydantic import BaseModel, Field, field_validator

from recoverai.domain.action import ActionType
from recoverai.domain.assessment import CauseCategory

# ---------------------------------------------------------
# Evidence Bundle (Input to LLM)
# ---------------------------------------------------------


class ObservedEventFact(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Observed event type")
    occurred_at: str = Field(..., description="ISO-8601 timestamp")
    error_code: str | None = Field(default=None)
    error_description: str | None = Field(default=None)
    payment_method: str | None = Field(default=None)
    source_type: str = Field(..., description="Origin source type")


class RecoveryEvidenceBundle(BaseModel):
    case_id: str = Field(..., description="Case identifier")
    revenue_source: str = Field(..., description="Source of revenue at risk")
    amount_formatted: str = Field(..., description="Transaction amount display")
    customer_id: str | None = Field(default=None)
    customer_failure_count: int = Field(default=0)
    has_systemic_signal: bool = Field(default=False)
    observed_events: list[ObservedEventFact] = Field(default_factory=list)
    prior_recovery_actions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------
# LLM Structured Outputs
# ---------------------------------------------------------


class EvidenceReferenceModel(BaseModel):
    source_id: str = Field(
        ..., description="The ID of the event providing evidence", min_length=1
    )


class CauseAssessmentModel(BaseModel):
    category: str = Field(..., description="Root cause category from CauseCategory")
    confidence: float = Field(
        ..., description="Estimated probability between 0.0 and 1.0"
    )
    confidence_meaning: str = Field(default="Model estimated probability")
    reasoning: str = Field(
        ..., min_length=5, description="Concrete case-specific explanation"
    )
    evidence_references: list[EvidenceReferenceModel] = Field(default_factory=list)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in CauseCategory.__members__:
            allowed = ", ".join(CauseCategory.__members__.keys())
            raise ValueError(
                f"Invalid cause category '{v}'. Allowed categories: {allowed}"
            )
        return clean

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError("Confidence must be a numeric float")
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Confidence cannot be NaN or Infinity")
        if not (0.0 <= float(v) <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return float(v)


class InterventionCandidateModel(BaseModel):
    action_type: str = Field(..., description="Action from ActionType enum")
    confidence: float = Field(
        ..., description="Estimated recovery probability between 0.0 and 1.0"
    )
    confidence_meaning: str = Field(default="Model estimated recovery probability")
    reasoning: str = Field(
        ..., min_length=5, description="Concrete case-specific rationale"
    )
    evidence_references: list[EvidenceReferenceModel] = Field(default_factory=list)

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in ActionType.__members__:
            allowed = ", ".join(ActionType.__members__.keys())
            raise ValueError(f"Invalid action type '{v}'. Allowed actions: {allowed}")
        return clean

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError("Confidence must be a numeric float")
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Confidence cannot be NaN or Infinity")
        if not (0.0 <= float(v) <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return float(v)


class InterventionPlanResponseModel(BaseModel):
    candidates: list[InterventionCandidateModel] = Field(..., min_length=1)
