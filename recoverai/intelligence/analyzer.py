import uuid
from datetime import datetime, UTC
from typing import Any

from recoverai.domain.action import ActionType
from recoverai.domain.assessment import AnalysisType, CauseAssessment, RiskAssessment
from recoverai.domain.case import RecoveryCase
from recoverai.domain.event import RevenueEvent
from recoverai.domain.evidence import EvidenceReference, Probability
from recoverai.domain.plan import (
    CandidateStatus,
    InterventionCandidate,
    InterventionPlan,
)
from recoverai.intelligence.gateway import LLMGateway


class RevenueIntelligenceAnalyzer:
    """
    Core engine for P06. Maps facts to risk, cause, and intervention plans.
    """

    def __init__(self, llm_gateway: LLMGateway | None = None):
        self.llm_gateway = llm_gateway

    def analyze(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any] | None = None,
    ) -> tuple[RiskAssessment, CauseAssessment, InterventionPlan]:
        ctx = context or {}

        # 1. Feature Construction
        features = self._extract_features(events, ctx)

        # 2. Risk Assessment (Deterministic base)
        risk = self._assess_risk(case, features, events)

        # 3. Cause Assessment
        cause = None
        if self.llm_gateway:
            try:
                cause = self.llm_gateway.synthesize_cause(case, events, ctx)
            except Exception:
                cause = None  # Fallback

        if not cause:
            cause = self._deterministic_cause_assessment(case, features, events)

        # 4. Intervention Candidates & Plan
        plan = None
        if self.llm_gateway:
            try:
                candidates = self.llm_gateway.generate_intervention_candidates(
                    case, events, ctx, cause
                )
                if candidates:
                    plan = self._build_plan_from_candidates(case, candidates, "LLM_1.0")
            except Exception:
                plan = None

        if not plan:
            plan = self._deterministic_intervention_plan(case, risk, cause, events)

        return risk, cause, plan

    def _extract_features(
        self, events: list[RevenueEvent], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalizes raw event inputs into analyzable signals.
        """
        return {
            "has_systemic_signal": context.get("active_downtime", False),
            "customer_failure_count": context.get("customer_failure_count", 1),
            "recent_events_count": len(events),
        }

    def _assess_risk(
        self, case: RecoveryCase, features: dict[str, Any], events: list[RevenueEvent]
    ) -> RiskAssessment:
        # Simple deterministic heuristic
        prob_val = 0.8
        if features.get("has_systemic_signal"):
            prob_val = 0.1
        elif features.get("customer_failure_count", 0) > 3:
            prob_val = 0.4

        return RiskAssessment(
            assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
            case_id=case.case_id,
            recovery_probability=Probability(prob_val, "expected recovery probability"),
            expected_recovery_value=case.amount_at_risk,
            model_name="deterministic_baseline",
            model_version="1.0",
            created_at=datetime.now(UTC),
        )

    def _deterministic_cause_assessment(
        self, case: RecoveryCase, features: dict[str, Any], events: list[RevenueEvent]
    ) -> CauseAssessment:
        from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType

        cat = "CUSTOMER_SPECIFIC"
        if features.get("has_systemic_signal"):
            cat = "SYSTEMIC_DEGRADATION"

        evidence = []
        for e in events:
            evidence.append(
                EvidenceReference(
                    source_type=EvidenceSourceType.RAZORPAY_EVENT,
                    source_id=e.event_id.value,
                    observed_at=e.occurred_at,
                    field="event_type",
                )
            )

        return CauseAssessment(
            cause_assessment_id=f"cause_{uuid.uuid4().hex[:8]}",
            case_id=case.case_id,
            category=cat,
            confidence=Probability(0.9, "cause confidence"),
            analysis_type=AnalysisType.RULE_BASED,
            model_version="1.0",
            created_at=datetime.now(UTC),
            evidence_references=evidence,
        )

    def _build_plan_from_candidates(
        self, case: RecoveryCase, candidates: list[InterventionCandidate], version: str
    ) -> InterventionPlan:
        selected = None
        best_ev = -1.0

        # Simple selection: max expected value * prob
        for cand in candidates:
            if cand.eligibility_status == CandidateStatus.PROPOSED:
                ev = (
                    float(cand.expected_recovery_value.amount_minor)
                    * cand.expected_recovery_probability.value
                )
                if ev > best_ev:
                    best_ev = ev
                    selected = cand.action_type

        return InterventionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            case_id=case.case_id,
            candidates=candidates,
            selected_action_type=selected,
            selection_reason="Highest expected value",
            selection_model_version=version,
            created_at=datetime.now(UTC),
            expected_recovery_value=case.amount_at_risk,
        )

    def _deterministic_intervention_plan(
        self,
        case: RecoveryCase,
        risk: RiskAssessment,
        cause: CauseAssessment,
        events: list[RevenueEvent],
    ) -> InterventionPlan:
        from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType

        evidence = []
        for e in events:
            evidence.append(
                EvidenceReference(
                    source_type=EvidenceSourceType.RAZORPAY_EVENT,
                    source_id=e.event_id.value,
                    observed_at=e.occurred_at,
                    field="event_type",
                )
            )

        candidates = []

        if cause.category == "SYSTEMIC_DEGRADATION":
            # Just wait
            candidates.append(
                InterventionCandidate(
                    candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
                    case_id=case.case_id,
                    action_type=ActionType.WAIT,
                    expected_recovery_probability=Probability(0.9, "success prob"),
                    expected_recovery_value=case.amount_at_risk,
                    eligibility_status=CandidateStatus.PROPOSED,
                    reason="Systemic degradation active",
                    evidence_references=evidence,
                )
            )
        else:
            candidates.append(
                InterventionCandidate(
                    candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
                    case_id=case.case_id,
                    action_type=ActionType.CREATE_PAYMENT_LINK,
                    expected_recovery_probability=Probability(0.7, "success prob"),
                    expected_recovery_value=case.amount_at_risk,
                    eligibility_status=CandidateStatus.PROPOSED,
                    reason="Standard recovery procedure",
                    evidence_references=evidence,
                )
            )

        return self._build_plan_from_candidates(case, candidates, "deterministic_1.0")
