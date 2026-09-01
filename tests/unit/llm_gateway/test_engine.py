import json
from datetime import UTC, datetime

import pytest

from recoverai.domain.action import ActionType
from recoverai.domain.case import RecoveryCase, RevenueSource
from recoverai.domain.event import (
    EventSource,
    EventSourceType,
    RevenueEvent,
    RevenueEventType,
)
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.intelligence.gateway import GatewayError
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from recoverai.llm_gateway.providers import MockProvider


@pytest.fixture
def dummy_case():
    return RecoveryCase(
        case_id=RecoveryCaseId("case_1"),
        merchant_id=MerchantId("m1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(1000, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
    )


@pytest.fixture
def dummy_event():
    return RevenueEvent(
        event_id=RevenueEventId("evt_1"),
        merchant_id=MerchantId("m1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        occurred_at=datetime.now(UTC),
        received_at=datetime.now(UTC),
        source=EventSource(
            source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="test"
        ),
    )


def test_successful_structured_response(dummy_case, dummy_event):
    valid_json = json.dumps(
        {
            "category": "INSUFFICIENT_FUNDS",
            "confidence": 0.95,
            "reasoning": "Sufficient evidence available",
            "evidence_references": [{"source_id": "evt_1"}],
        }
    )
    provider = MockProvider("mock1", [valid_json])
    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[provider])

    cause = gateway.synthesize_cause(dummy_case, [dummy_event], {})
    assert cause is not None
    assert cause.category == "INSUFFICIENT_FUNDS"
    assert cause.confidence.value == 0.95
    assert len(cause.evidence_references) == 1
    assert cause.evidence_references[0].source_id == "evt_1"
    assert provider.calls == 1


def test_fallback_behavior_on_provider_error(dummy_case, dummy_event):
    valid_json = json.dumps(
        {
            "category": "INSUFFICIENT_FUNDS",
            "confidence": 0.95,
            "reasoning": "Valid",
            "evidence_references": [],
        }
    )
    p1 = MockProvider("mock1", fail_count=1)
    p2 = MockProvider("mock2", [valid_json])

    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1, p2])
    cause = gateway.synthesize_cause(dummy_case, [dummy_event], {})

    assert cause is not None
    assert p1.calls == 1
    assert p2.calls == 1


def test_all_providers_fail(dummy_case):
    p1 = MockProvider("mock1", fail_count=1)
    p2 = MockProvider("mock2", fail_count=1)

    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1, p2])
    with pytest.raises(GatewayError, match="All providers failed"):
        gateway.synthesize_cause(dummy_case, [], {})


def test_invalid_schema_triggers_fallback(dummy_case, dummy_event):
    invalid_json = '{"confidence": 0.95}'
    valid_json = json.dumps(
        {
            "category": "CARD_EXPIRED",
            "confidence": 0.8,
            "reasoning": "Valid",
            "evidence_references": [],
        }
    )

    p1 = MockProvider("mock1", [invalid_json])
    p2 = MockProvider("mock2", [valid_json])

    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1, p2])
    cause = gateway.synthesize_cause(dummy_case, [dummy_event], {})

    assert cause is not None
    assert cause.category == "CARD_EXPIRED"
    assert p1.calls == 1
    assert p2.calls == 1


def test_malformed_json(dummy_case, dummy_event):
    malformed = "{ broken json"
    valid = json.dumps(
        {
            "category": "CARD_EXPIRED",
            "confidence": 1.0,
            "reasoning": "Valid",
            "evidence_references": [],
        }
    )

    p1 = MockProvider("mock1", [malformed])
    p2 = MockProvider("mock2", [valid])
    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1, p2])

    cause = gateway.synthesize_cause(dummy_case, [dummy_event], {})
    assert cause.category == "CARD_EXPIRED"


def test_invalid_enum_fails_safely(dummy_case):
    invalid_enum = json.dumps(
        {
            "candidates": [
                {
                    "action_type": "HACK_SYSTEM",
                    "confidence": 0.5,
                    "reasoning": "Invalid",
                    "evidence_references": [],
                }
            ]
        }
    )
    p1 = MockProvider("mock1", [invalid_enum])
    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1])

    with pytest.raises(GatewayError):
        gateway.generate_intervention_candidates(dummy_case, [], {}, None)


def test_invalid_probability_fails_safely(dummy_case):
    invalid_prob = json.dumps(
        {
            "category": "FOO",
            "confidence": 1.5,
            "reasoning": "Invalid",
            "evidence_references": [],
        }
    )
    p1 = MockProvider("mock1", [invalid_prob])
    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1])
    with pytest.raises(GatewayError):
        gateway.synthesize_cause(dummy_case, [], {})


def test_generate_intervention_candidates_success(dummy_case):
    valid_json = json.dumps(
        {
            "candidates": [
                {
                    "action_type": "CREATE_PAYMENT_LINK",
                    "confidence": 0.8,
                    "reasoning": "Appropriate action",
                    "evidence_references": [],
                }
            ]
        }
    )
    p1 = MockProvider("mock1", [valid_json])
    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1])

    provider, candidates = gateway.generate_intervention_candidates(dummy_case, [], {}, None)
    assert len(candidates) == 1
    assert candidates[0].action_type == ActionType.CREATE_PAYMENT_LINK
    assert candidates[0].expected_recovery_value == dummy_case.amount_at_risk


def test_llm_currency_hallucination_mismatch(dummy_case, dummy_event):
    invalid_currency_json = json.dumps(
        {
            "candidates": [
                {
                    "action_type": "CREATE_PAYMENT_LINK",
                    "confidence": 0.85,
                    "expected_recovery_value_minor": 1000,
                    "expected_recovery_currency": "INVALID_CURRENCY",
                    "evidence_references": [],
                }
            ]
        }
    )
    p1 = MockProvider("mock_bad_currency", [invalid_currency_json])
    gateway = ConcreteLLMGateway(GatewayConfig(), providers=[p1])

    with pytest.raises(GatewayError, match="All providers failed"):
        gateway.generate_intervention_candidates(dummy_case, [dummy_event], {}, None)
