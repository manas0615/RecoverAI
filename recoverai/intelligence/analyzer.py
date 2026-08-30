import uuid
from datetime import UTC, datetime
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
from recoverai.intelligence.gateway import GatewayError, LLMGateway


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
                if cause:
                    self._sanitize_cause_evidence(cause, events)
            except (ValueError, GatewayError):
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
                    self._sanitize_candidates_evidence(candidates, events)
                    plan = self._build_plan_from_candidates(case, candidates, "LLM_1.0")
            except (ValueError, GatewayError):
                plan = None

        if not plan:
            plan = self._deterministic_intervention_plan(case, risk, cause, events)

        return risk, cause, plan

    def _sanitize_cause_evidence(
        self, cause: CauseAssessment, events: list[RevenueEvent]
    ) -> None:
        valid_ids = {e.event_id.value for e in events}
        valid_evidence = [
            ev for ev in cause.evidence_references if ev.source_id in valid_ids
        ]
        object.__setattr__(cause, "evidence_references", valid_evidence)

    def _sanitize_candidates_evidence(
        self, candidates: list[InterventionCandidate], events: list[RevenueEvent]
    ) -> None:
        valid_ids = {e.event_id.value for e in events}
        for cand in candidates:
            valid_evidence = [
                ev for ev in cand.evidence_references if ev.source_id in valid_ids
            ]
            object.__setattr__(cand, "evidence_references", valid_evidence)

    def _extract_features(
        self, events: list[RevenueEvent], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalizes raw event inputs into analyzable signals.
        """
        # Determine systemic signal from events (e.g. multiple failures in a short time, or provider errors)
        has_systemic = context.get("active_downtime", False)
        customer_failures = context.get("customer_failure_count", 0)
        recent_events = len(events)
        
        # Check event types
        event_types = [e.event_type.value for e in events]
        if "PAYMENT_FAILED" in event_types and "PAYMENT_LINK_FAILED" in event_types:
            customer_failures += 2
        
        # Determine if there's an explicit error from provider in events (like 'BAD_REQUEST' etc.)
        for e in events:
            if e.metadata and e.metadata.get("error_code") in ("GATEWAY_ERROR", "BAD_REQUEST", "SERVER_ERROR"):
                has_systemic = True

        return {
            "has_systemic_signal": has_systemic,
            "customer_failure_count": customer_failures,
            "recent_events_count": recent_events,
            "event_types": event_types,
        }

    def _assess_risk(
        self, case: RecoveryCase, features: dict[str, Any], events: list[RevenueEvent]
    ) -> RiskAssessment:
        # P22: Explainable deterministic heuristic
        prob_val = 0.85 # Baseline

        if features.get("has_systemic_signal"):
            prob_val -= 0.60
        else:
            failures = features.get("customer_failure_count", 0)
            if failures > 0:
                prob_val -= (failures * 0.15)
                
        # Clamp
        prob_val = max(0.0, min(1.0, prob_val))

        return RiskAssessment(
            assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
            case_id=case.case_id,
            recovery_probability=Probability(prob_val, "Derived from historical failure count and systemic signals"),
            expected_recovery_value=case.amount_at_risk,
            model_name="deterministic_baseline",
            model_version="1.0",
            created_at=datetime.now(UTC),
        )

    def _deterministic_cause_assessment(
        self, case: RecoveryCase, features: dict[str, Any], events: list[RevenueEvent]
    ) -> CauseAssessment:
        from recoverai.domain.evidence import EvidenceSourceType

        if features.get("has_systemic_signal"):
            cat = "SYSTEMIC_DEGRADATION"
            conf = 0.95
        elif features.get("customer_failure_count", 0) >= 2:
            cat = "INSUFFICIENT_FUNDS"
            conf = 0.80
        else:
            cat = "CUSTOMER_SPECIFIC"
            conf = 0.70

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
            confidence=Probability(conf, "cause confidence"),
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
        reason = ""
        expected_value = case.amount_at_risk

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
                    reason = cand.reason
                    expected_value = cand.expected_recovery_value

        return InterventionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            case_id=case.case_id,
            candidates=candidates,
            selected_action_type=selected,
            selection_reason=reason or "Highest expected value",
            selection_model_version=version,
            created_at=datetime.now(UTC),
            expected_recovery_value=expected_value,
        )

    def _deterministic_intervention_plan(
        self,
        case: RecoveryCase,
        risk: RiskAssessment,
        cause: CauseAssessment,
        events: list[RevenueEvent],
    ) -> InterventionPlan:
        from recoverai.domain.evidence import EvidenceSourceType
        from recoverai.domain.money import Money, RevenueAmount

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
        # Calculate expected value (Prob * Amount)
        base_amount = case.amount_at_risk.amount_minor
        currency = case.amount_at_risk.currency
        
        # P22: Intervention economics
        if cause.category == "SYSTEMIC_DEGRADATION":
            ev = int(base_amount * 0.9)
            candidates.append(
                InterventionCandidate(
                    candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
                    case_id=case.case_id,
                    action_type=ActionType.WAIT,
                    expected_recovery_probability=Probability(0.9, "Wait success prob"),
                    expected_recovery_value=RevenueAmount(Money(ev, currency)),
                    eligibility_status=CandidateStatus.PROPOSED,
                    reason="Systemic degradation active. Waiting avoids unnecessary friction and failures.",
                    evidence_references=evidence,
                )
            )
        else:
            ev = int(base_amount * risk.recovery_probability.value)
            candidates.append(
                InterventionCandidate(
                    candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
                    case_id=case.case_id,
                    action_type=ActionType.CREATE_PAYMENT_LINK,
                    expected_recovery_probability=risk.recovery_probability,
                    expected_recovery_value=RevenueAmount(Money(ev, currency)),
                    eligibility_status=CandidateStatus.PROPOSED,
                    reason=f"Standard recovery procedure. Expected value: {(ev/100):.2f} {currency.value}.",
                    evidence_references=evidence,
                )
            )

        return self._build_plan_from_candidates(case, candidates, "deterministic_1.0")
