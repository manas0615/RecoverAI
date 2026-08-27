from pydantic import BaseModel, Field


class EvidenceReferenceModel(BaseModel):
    source_id: str = Field(..., description="The ID of the event providing evidence")


class CauseAssessmentModel(BaseModel):
    category: str = Field(..., description="E.g., INSUFFICIENT_FUNDS, CARD_EXPIRED")
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_meaning: str = Field(default="Model estimated probability")
    evidence_references: list[EvidenceReferenceModel] = Field(default_factory=list)


class InterventionCandidateModel(BaseModel):
    action_type: str = Field(
        ..., description="E.g., RETRY_PAYMENT, CREATE_PAYMENT_LINK, SEND_EMAIL"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_meaning: str = Field(default="Model estimated success probability")
    expected_recovery_value_minor: int = Field(..., ge=0)
    expected_recovery_currency: str = Field(..., min_length=3, max_length=3)
    evidence_references: list[EvidenceReferenceModel] = Field(default_factory=list)
