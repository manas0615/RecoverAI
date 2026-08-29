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
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
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
from .schemas import CauseAssessmentModel, InterventionCandidateModel

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

    def _build_evidence(
        self, refs: list, events: list[RevenueEvent]
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
        prompt = self._build_cause_prompt(case, events, context)
        schema = CauseAssessmentModel.model_json_schema()

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
                raise
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
        cause: CauseAssessment,
    ) -> list[InterventionCandidate]:
        prompt = self._build_plan_prompt(case, events, context, cause)
        schema = {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": InterventionCandidateModel.model_json_schema(),
                }
            },
            "required": ["candidates"],
        }

        for provider in self.providers:
            try:
                raw_json = provider.generate_json(prompt, schema=schema)
                data = json.loads(raw_json)

                candidates = []
                for idx, item in enumerate(data.get("candidates", [])):
                    model = InterventionCandidateModel.model_validate(item)
                    evidence = self._build_evidence(model.evidence_references, events)
                    candidates.append(
                        InterventionCandidate(
                            candidate_id=f"cand_{idx}",
                            case_id=case.case_id,
                            action_type=ActionType(model.action_type),
                            expected_recovery_probability=Probability(
                                model.confidence, meaning=model.confidence_meaning
                            ),
                            expected_recovery_value=RevenueAmount(
                                Money(
                                    model.expected_recovery_value_minor,
                                    CurrencyCode(model.expected_recovery_currency),
                                )
                            ),
                            eligibility_status=CandidateStatus.PROPOSED,
                            evidence_references=evidence,
                        )
                    )
                return candidates
            except ConfigurationError as e:
                logger.error(f"Provider {provider.name} configuration failed: {e}")
                raise
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

    def _build_cause_prompt(
        self, case: RecoveryCase, events: list[RevenueEvent], context: dict[str, Any]
    ) -> str:
        event_types = ", ".join([e.event_type.value for e in events])
        return (
            f"Analyze the root cause for revenue recovery case {case.case_id.value}. "
            f"The case involves a failed payment of {case.amount_at_risk.amount_minor} {case.amount_at_risk.currency.value}. "
            f"The following events occurred: {event_types}. "
            f"Given the context: {context}, determine the likely cause category (e.g., CUSTOMER_SPECIFIC, SYSTEMIC_DEGRADATION), "
            f"a confidence score between 0.0 and 1.0, and a concise explanation."
        )

    def _build_plan_prompt(
        self,
        case: RecoveryCase,
        events: list[RevenueEvent],
        context: dict[str, Any],
        cause: CauseAssessment | None,
    ) -> str:
        event_types = ", ".join([e.event_type.value for e in events])
        cause_str = (
            f"The determined cause is {cause.category} with {cause.confidence.value} confidence. "
            if cause
            else "No cause determined. "
        )
        return (
            f"Generate an intervention plan for revenue recovery case {case.case_id.value}. "
            f"The case involves {case.amount_at_risk.amount_minor} {case.amount_at_risk.currency.value}. "
            f"{cause_str}"
            f"Events: {event_types}. "
            f"Select the best action (e.g., CREATE_PAYMENT_LINK, WAIT, ESCALATE), "
            f"an expected recovery value in minor units, a success probability, and a concise reason."
        )
