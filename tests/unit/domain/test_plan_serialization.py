import json
from datetime import UTC, datetime

from recoverai.domain.action import ActionType
from recoverai.domain.case import RevenueAmount
from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType, Probability
from recoverai.domain.identifiers import RecoveryCaseId
from recoverai.domain.money import CurrencyCode, Money
from recoverai.domain.plan import (
    CandidateStatus,
    InterventionCandidate,
    InterventionPlan,
)


def test_plan_serialization_round_trip():
    case_id = RecoveryCaseId("case_123")

    ref1 = EvidenceReference(
        source_type=EvidenceSourceType.RAZORPAY_PAYMENT,
        source_id="pay_999",
        observed_at=datetime(2026, 8, 30, 10, 0, 0, tzinfo=UTC),
        field="status",
    )

    candidate = InterventionCandidate(
        candidate_id="cand_abc",
        case_id=case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        expected_recovery_probability=Probability(
            value=0.85, meaning="Based on success rate"
        ),
        expected_recovery_value=RevenueAmount(Money(1500, CurrencyCode.INR)),
        eligibility_status=CandidateStatus.PROPOSED,
        intervention_cost=RevenueAmount(Money(100, CurrencyCode.INR)),
        friction_score=0.1,
        risk_score=0.2,
        reason="Recoverable failure",
        evidence_references=[ref1],
    )

    plan = InterventionPlan(
        plan_id="plan_xyz",
        case_id=case_id,
        candidates=[candidate],
        selected_action_type=ActionType.CREATE_PAYMENT_LINK,
        selection_reason="Best candidate",
        selection_model_version="gemini-3.5-flash",
        created_at=datetime(2026, 8, 30, 11, 0, 0, tzinfo=UTC),
        expected_recovery_value=RevenueAmount(Money(1500, CurrencyCode.INR)),
    )

    # Serialize
    plan_dict = plan.to_dict()
    assert plan_dict["schema_version"] == 1
    assert plan_dict["plan_id"] == "plan_xyz"
    assert plan_dict["case_id"] == "case_123"

    # Convert to JSON string (simulating database snapshot storage)
    json_str = json.dumps(plan_dict)

    # Deserialize
    loaded_dict = json.loads(json_str)
    reconstructed_plan = InterventionPlan.from_dict(loaded_dict)

    # Assertions
    assert reconstructed_plan.plan_id == plan.plan_id
    assert reconstructed_plan.case_id == plan.case_id
    assert reconstructed_plan.selected_action_type == plan.selected_action_type
    assert reconstructed_plan.selection_reason == plan.selection_reason
    assert reconstructed_plan.selection_model_version == plan.selection_model_version
    assert reconstructed_plan.created_at == plan.created_at
    assert reconstructed_plan.expected_recovery_value == plan.expected_recovery_value

    assert len(reconstructed_plan.candidates) == 1
    loaded_cand = reconstructed_plan.candidates[0]
    assert loaded_cand.candidate_id == candidate.candidate_id
    assert loaded_cand.action_type == candidate.action_type
    assert (
        loaded_cand.expected_recovery_probability
        == candidate.expected_recovery_probability
    )
    assert loaded_cand.expected_recovery_value == candidate.expected_recovery_value
    assert loaded_cand.eligibility_status == candidate.eligibility_status
    assert loaded_cand.intervention_cost == candidate.intervention_cost
    assert loaded_cand.friction_score == candidate.friction_score
    assert loaded_cand.risk_score == candidate.risk_score
    assert loaded_cand.reason == candidate.reason

    assert len(loaded_cand.evidence_references) == 1
    loaded_ref = loaded_cand.evidence_references[0]
    assert loaded_ref.source_type == ref1.source_type
    assert loaded_ref.source_id == ref1.source_id
    assert loaded_ref.observed_at == ref1.observed_at
    assert loaded_ref.field == ref1.field
