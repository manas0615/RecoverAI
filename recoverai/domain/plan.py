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

    def to_dict(self) -> dict:
        return {
            "schema_version": 1,
            "plan_id": self.plan_id,
            "case_id": self.case_id.value,
            "selected_action_type": self.selected_action_type.value
            if self.selected_action_type
            else None,
            "selection_reason": self.selection_reason,
            "selection_model_version": self.selection_model_version,
            "created_at": self.created_at.isoformat(),
            "expected_recovery_value": {
                "amount_minor": self.expected_recovery_value.amount_minor,
                "currency": self.expected_recovery_value.currency.value,
            }
            if self.expected_recovery_value
            else None,
            "candidates": [
                {
                    "candidate_id": cand.candidate_id,
                    "case_id": cand.case_id.value,
                    "action_type": cand.action_type.value,
                    "expected_recovery_probability": {
                        "value": cand.expected_recovery_probability.value,
                        "meaning": cand.expected_recovery_probability.meaning,
                    },
                    "expected_recovery_value": {
                        "amount_minor": cand.expected_recovery_value.amount_minor,
                        "currency": cand.expected_recovery_value.currency.value,
                    },
                    "eligibility_status": cand.eligibility_status.value,
                    "intervention_cost": {
                        "amount_minor": cand.intervention_cost.amount_minor,
                        "currency": cand.intervention_cost.currency.value,
                    }
                    if cand.intervention_cost
                    else None,
                    "friction_score": cand.friction_score,
                    "risk_score": cand.risk_score,
                    "reason": cand.reason,
                    "evidence_references": [
                        {
                            "source_type": ref.source_type.value,
                            "source_id": ref.source_id,
                            "observed_at": ref.observed_at.isoformat(),
                            "field": ref.field,
                        }
                        for ref in cand.evidence_references
                    ],
                }
                for cand in self.candidates
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterventionPlan":
        from recoverai.domain.evidence import EvidenceSourceType
        from recoverai.domain.money import CurrencyCode, Money

        if data.get("schema_version") != 1:
            raise ValueError(
                f"Unsupported schema version: {data.get('schema_version')}"
            )

        created_at = datetime.fromisoformat(data["created_at"])
        expected_recovery_val = None
        if data.get("expected_recovery_value"):
            val_data = data["expected_recovery_value"]
            expected_recovery_val = RevenueAmount(
                Money(val_data["amount_minor"], CurrencyCode(val_data["currency"]))
            )

        candidates = []
        for cand_data in data["candidates"]:
            prob_data = cand_data["expected_recovery_probability"]
            val_data = cand_data["expected_recovery_value"]

            cost = None
            if cand_data.get("intervention_cost"):
                cost_data = cand_data["intervention_cost"]
                cost = RevenueAmount(
                    Money(
                        cost_data["amount_minor"],
                        CurrencyCode(cost_data["currency"]),
                    )
                )

            refs = [
                EvidenceReference(
                    source_type=EvidenceSourceType(ref["source_type"]),
                    source_id=ref["source_id"],
                    observed_at=datetime.fromisoformat(ref["observed_at"]),
                    field=ref.get("field"),
                )
                for ref in cand_data.get("evidence_references", [])
            ]

            candidates.append(
                InterventionCandidate(
                    candidate_id=cand_data["candidate_id"],
                    case_id=RecoveryCaseId(cand_data["case_id"]),
                    action_type=ActionType(cand_data["action_type"]),
                    expected_recovery_probability=Probability(
                        value=float(prob_data["value"]),
                        meaning=prob_data["meaning"],
                    ),
                    expected_recovery_value=RevenueAmount(
                        Money(
                            val_data["amount_minor"],
                            CurrencyCode(val_data["currency"]),
                        )
                    ),
                    eligibility_status=CandidateStatus(cand_data["eligibility_status"]),
                    intervention_cost=cost,
                    friction_score=cand_data.get("friction_score"),
                    risk_score=cand_data.get("risk_score"),
                    reason=cand_data.get("reason"),
                    evidence_references=refs,
                )
            )

        selected_action_type = None
        if data.get("selected_action_type"):
            selected_action_type = ActionType(data["selected_action_type"])

        return cls(
            plan_id=data["plan_id"],
            case_id=RecoveryCaseId(data["case_id"]),
            candidates=candidates,
            selected_action_type=selected_action_type,
            selection_reason=data["selection_reason"],
            selection_model_version=data["selection_model_version"],
            created_at=created_at,
            expected_recovery_value=expected_recovery_val,
        )
