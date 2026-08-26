from datetime import UTC, datetime

import pytest

from recoverai.domain import CurrencyCode, MerchantId, RevenueEventType
from recoverai.ingestion.exceptions import (
    MalformedWebhookPayload,
    UnsupportedWebhookEvent,
)
from recoverai.ingestion.razorpay.normalizer import RazorpayNormalizer


def test_normalize_payment_failed():
    now = datetime.now(UTC)
    payload = {
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_123",
                    "amount": 5000,
                    "currency": "INR",
                    "customer_id": "cust_abc",
                    "created_at": 1600000000,
                }
            }
        },
    }

    normalizer = RazorpayNormalizer()
    ev = normalizer.normalize(MerchantId("m_1"), payload, "evt_123", now)

    assert ev.event_type == RevenueEventType.PAYMENT_FAILED
    assert ev.source.source_event_id == "evt_123"
    assert ev.merchant_id.value == "m_1"
    assert ev.customer_id.value == "cust_abc"
    assert ev.amount.amount_minor == 5000
    assert ev.amount.currency == CurrencyCode.INR
    assert ev.external_reference == "pay_123"
    assert ev.occurred_at == datetime.fromtimestamp(1600000000, tz=UTC)
    assert ev.received_at == now


def test_normalize_unsupported_event():
    now = datetime.now(UTC)
    payload = {"event": "some.unsupported.event"}

    normalizer = RazorpayNormalizer()
    with pytest.raises(UnsupportedWebhookEvent):
        normalizer.normalize(MerchantId("m_1"), payload, "evt_123", now)


def test_normalize_malformed_payload():
    now = datetime.now(UTC)
    # Missing event key entirely
    payload = {"contains": ["payment"]}

    normalizer = RazorpayNormalizer()
    with pytest.raises(MalformedWebhookPayload):
        normalizer.normalize(MerchantId("m_1"), payload, "evt_123", now)


@pytest.mark.parametrize(
    "razorpay_event,expected_type",
    [
        ("payment.authorized", RevenueEventType.PAYMENT_AUTHORIZED),
        ("payment.captured", RevenueEventType.PAYMENT_CAPTURED),
        ("payment_link.paid", RevenueEventType.PAYMENT_LINK_PAID),
        ("payment.downtime.started", RevenueEventType.PAYMENT_DEGRADATION_SIGNAL),
        ("payment.downtime.updated", RevenueEventType.PAYMENT_DEGRADATION_SIGNAL),
    ],
)
def test_normalize_supported_events(razorpay_event, expected_type):
    now = datetime.now(UTC)
    payload = {
        "event": razorpay_event,
        "contains": ["payment"],
        "payload": {"payment": {"entity": {"id": "pay_123", "created_at": 1600000000}}},
    }
    normalizer = RazorpayNormalizer()
    ev = normalizer.normalize(MerchantId("m_1"), payload, "evt_123", now)
    assert ev.event_type == expected_type
