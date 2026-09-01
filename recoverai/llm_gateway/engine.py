import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError

from recoverai.domain.action import ActionType
from recoverai.domain.assessment import AnalysisType, CauseAssessment
from recoverai.domain.case import RecoveryCase
from recoverai.domain.event import RevenueEvent
from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType, Probability
from recoverai.domain.plan import CandidateStatus, InterventionCandidate
from recoverai.intelligence.gateway import GatewayError, LLMGateway

from .config import GatewayConfig
from .providers import (
    ConfigurationError,
    GeminiAdapter,
    GroqAdapter,
    HuggingFaceAdapter,
    ProviderAdapter,
    ProviderError,
)
from .schemas import (
    CauseAssessmentModel,
    EvidenceReferenceModel,
    InterventionPlanResponseModel,
    ObservedEventFact,
    RecoveryEvidenceBundle,
)

logger = logging.getLogger(__name__)


class ConcreteLLMGateway(LLMGateway):
    def __init__(
        self, config: GatewayConfig, providers: list[ProviderAdapter] | None = None
    ):
        self.config = config
        if providers is not None:
            self.providers = providers
        else:
            self.providers = [
                GeminiAdapter(config.gemini_api_key, config.gemini_model),
                GroqAdapter(config.groq_api_key, config.groq_model),
                HuggingFaceAdapter(config.hf_api_key, config.hf_model),
            ]

    def _build_evidence_bundle(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
    ) -> RecoveryEvidenceBundle:
        major_units = case.amount_at_risk.amount_minor / 100.0
        amount_str = f"{major_units:.2f} {case.amount_at_risk.currency.value}"

        sorted_events = sorted(events, key=lambda e: e.occurred_at)
        observed_events: list[ObservedEventFact] = []
        for e in sorted_events:
            meta = dict(e.metadata) if e.metadata else {}
            err_code = meta.get("error_code") or meta.get("code") or meta.get("reason")
            err_desc = (
                meta.get("error_description")
                or meta.get("description")
                or meta.get("error_reason")
            )
            pay_method = meta.get("payment_method") or meta.get("method")

            observed_events.append(
                ObservedEventFact(
                    event_id=e.event_id.value,
                    event_type=e.event_type.value,
                    occurred_at=e.occurred_at.isoformat(),
                    error_code=str(err_code) if err_code is not None else None,
                    error_description=str(err_desc) if err_desc is not None else None,
                    payment_method=str(pay_method) if pay_method is not None else None,
                    source_type=e.source.source_type.value,
                )
            )

        systemic = bool(
            context.get("active_downtime", False)
            or context.get("has_systemic_signal", False)
        )
        failure_count = int(context.get("customer_failure_count", 0))
        prior_actions = [str(a) for a in context.get("prior_recovery_actions", [])]

        return RecoveryEvidenceBundle(
            case_id=case.case_id.value,
            revenue_source=case.revenue_source.value,
            amount_formatted=amount_str,
            customer_id=case.customer_id.value if case.customer_id else None,
            customer_failure_count=failure_count,
            has_systemic_signal=systemic,
            observed_events=observed_events,
            prior_recovery_actions=prior_actions,
        )

    def _build_evidence(
        self, refs: list[EvidenceReferenceModel], events: list[RevenueEvent]
    ) -> list[EvidenceReference]:
        event_map = {e.event_id.value: e for e in events}
        evidence = []
        for ref in refs:
            event = event_map.get(ref.source_id)
            if event:
                evidence.append(
                    EvidenceReference(
                        source_type=EvidenceSourceType.RAZORPAY_EVENT,
                        source_id=event.event_id.value,
                        observed_at=event.occurred_at,
                    )
                )
        return evidence

    def synthesize_cause(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
    ) -> CauseAssessment | None:
        evidence_bundle = self._build_evidence_bundle(case, events, context)
        prompt = self._build_cause_prompt(evidence_bundle)
        schema = {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "confidence": {"type": "number"},
                "confidence_meaning": {"type": "string"},
                "reasoning": {"type": "string"},
                "evidence_references": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"source_id": {"type": "string"}},
                        "required": ["source_id"],
                    },
                },
            },
            "required": ["category", "confidence", "reasoning", "evidence_references"],
        }

        for provider in self.providers:
            try:
                raw_json = provider.generate_json(prompt, schema=schema)
                model = CauseAssessmentModel.model_validate_json(raw_json)
                evidence = self._build_evidence(model.evidence_references, events)

                return CauseAssessment(
                    cause_assessment_id=f"cause_{uuid.uuid4().hex[:8]}",
                    case_id=case.case_id,
                    category=model.category,
                    confidence=Probability(
                        model.confidence, meaning=model.confidence_meaning
                    ),
                    analysis_type=AnalysisType.LLM,
                    model_version=f"{provider.name}-latest",
                    created_at=datetime.now(UTC),
                    evidence_references=evidence,
                )
            except ConfigurationError as e:
                logger.error(f"Provider {provider.name} configuration failed: {e}")
                continue
            except (
                json.JSONDecodeError,
                ValidationError,
                ProviderError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue

        raise GatewayError("All providers failed to synthesize cause.")

    def generate_intervention_candidates(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
        cause: CauseAssessment | None,
    ) -> tuple[str, list[InterventionCandidate]]:
        evidence_bundle = self._build_evidence_bundle(case, events, context)
        prompt = self._build_plan_prompt(evidence_bundle, cause)
        schema = {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action_type": {"type": "string"},
                            "confidence": {"type": "number"},
                            "confidence_meaning": {"type": "string"},
                            "reasoning": {"type": "string"},
                            "evidence_references": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"source_id": {"type": "string"}},
                                    "required": ["source_id"],
                                },
                            },
                        },
                        "required": [
                            "action_type",
                            "confidence",
                            "reasoning",
                            "evidence_references",
                        ],
                    },
                }
            },
            "required": ["candidates"],
        }

        for provider in self.providers:
            try:
                raw_json = provider.generate_json(prompt, schema=schema)
                plan_response = InterventionPlanResponseModel.model_validate_json(
                    raw_json
                )

                candidates = []
                for idx, model in enumerate(plan_response.candidates):
                    evidence = self._build_evidence(model.evidence_references, events)
                    candidates.append(
                        InterventionCandidate(
                            candidate_id=f"cand_{idx}",
                            case_id=case.case_id,
                            action_type=ActionType(model.action_type),
                            expected_recovery_probability=Probability(
                                model.confidence, meaning=model.confidence_meaning
                            ),
                            expected_recovery_value=case.amount_at_risk,
                            eligibility_status=CandidateStatus.PROPOSED,
                            reason=model.reasoning,
                            evidence_references=evidence,
                        )
                    )
                return (provider.name.capitalize(), candidates)
            except ConfigurationError as e:
                logger.error(f"Provider {provider.name} configuration failed: {e}")
                continue
            except (
                json.JSONDecodeError,
                ValidationError,
                ProviderError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue

        raise GatewayError("All providers failed to generate intervention candidates.")

    def _build_cause_prompt(self, evidence: RecoveryEvidenceBundle) -> str:
        evidence_json = evidence.model_dump_json(indent=2)
        return f"""You are the Root Cause Analysis Engine for RecoverAI, an autonomous revenue recovery system.
Analyze the following strictly-typed evidence bundle containing observed telemetry facts and determine the root cause for the revenue recovery case.

### EVIDENCE BUNDLE (OBSERVED FACTS ONLY):
{evidence_json}

### INSTRUCTIONS & CONSTRAINTS:
1. STRICT FACTUAL GROUNDING: Base your evaluation solely on the facts provided in the evidence bundle above. Do not assume or invent facts.
2. EVIDENCE CITATION: For every observation supporting your conclusion, cite its exact `event_id` in `evidence_references`.
3. NO FINANCIAL CALCULATIONS: Do not output, estimate, or modify financial amounts, recovery values, or currency codes.
4. ANTI-HALLUCINATION & ANTI-BOILERPLATE:
   - Provide a clear, concrete, case-specific `reasoning` (1-3 sentences) linking specific error codes, failure counts, or systemic signals to your conclusion. Explain WHY this is the cause FOR THIS case BASED ON WHICH evidence.
   - Strictly FORBIDDEN generic phrases: "Highest expected value", "Standard recovery procedure", "Optimal strategy", "Based on the data provided", "As an AI model", or restating the prompt.
5. ROOT CAUSE TAXONOMY: Output a valid `category` string matching one of:
   - CUSTOMER_SPECIFIC, SYSTEMIC_DEGRADATION, INSUFFICIENT_FUNDS, CARD_EXPIRED, AUTHENTICATION_FAILED, TECHNICAL_ERROR, UNKNOWN
6. CONFIDENCE: Provide a numeric `confidence` between 0.0 and 1.0 representing empirical confidence given the evidence quality.

Return ONLY a valid JSON object matching the requested schema. If evidence is insufficient, use category UNKNOWN and state "Insufficient evidence to determine cause." in reasoning.
"""

    def _build_plan_prompt(
        self,
        evidence: RecoveryEvidenceBundle,
        cause: CauseAssessment | None,
    ) -> str:
        evidence_json = evidence.model_dump_json(indent=2)
        cause_summary = (
            f"Category: {cause.category}, Confidence: {cause.confidence.value:.2f}"
            if cause
            else "None determined"
        )
        return f"""You are the Intervention Strategy Engine for RecoverAI, an autonomous revenue recovery system.
Evaluate potential recovery intervention candidate actions for the case based strictly on the provided evidence bundle and cause assessment.

### EVIDENCE BUNDLE (OBSERVED FACTS ONLY):
{evidence_json}

### DETERMINED ROOT CAUSE:
{cause_summary}

### INSTRUCTIONS & CONSTRAINTS:
1. STRICT FACTUAL GROUNDING: Base every recommended action solely on the observed events, error codes, prior attempts, and systemic signals.
2. ACTION TAXONOMY: Each candidate `action_type` MUST be one of:
   - WAIT, CREATE_PAYMENT_LINK, SEND_PAYMENT_LINK_NOTIFICATION, PAYMENT_LINK_REMINDER, ESCALATE, SUPPRESS
3. NO FINANCIAL OUTPUTS: Do NOT output recovery amounts, expected currency, or minor unit values.
4. CASE-SPECIFIC RATIONALE: The `reasoning` field for each candidate MUST detail the specific telemetry fact that justifies the action. Explain WHY this intervention FOR THIS case BASED ON WHICH evidence.
   - Strictly FORBIDDEN generic phrases: "Highest expected value", "Standard recovery procedure", "Optimal action", "Best course of action", or generic filler text.
5. EVIDENCE CITATION: Populate `evidence_references` with the exact `event_id`s from `observed_events` that justify this candidate action.
6. SUCCESS PROBABILITY: Provide a numeric `confidence` score between 0.0 and 1.0 reflecting realistic recovery likelihood under this action.

Return ONLY a valid JSON object with the `candidates` array matching the requested schema.
"""
