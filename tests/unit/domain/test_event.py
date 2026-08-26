from datetime import UTC, datetime, timedelta

import pytest

from recoverai.domain.event import (
    EventSource,
    EventSourceType,
    RevenueEvent,
    RevenueEventType,
)
from recoverai.domain.identifiers import CustomerId, MerchantId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money


def test_event_source():
    src = EventSource(
        source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="ext_123"
    )
    assert src.source_type == EventSourceType.RAZORPAY_WEBHOOK
    assert src.source_event_id == "ext_123"


def test_revenue_event_valid_construction():
    now = datetime.now(UTC)
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, "ext_1"),
        merchant_id=MerchantId("m_1"),
        occurred_at=now - timedelta(minutes=1),
        received_at=now,
        customer_id=CustomerId("c_1"),
        amount=Money(1000, CurrencyCode.INR),
    )
    assert ev.event_type == RevenueEventType.PAYMENT_FAILED
    assert ev.amount.amount_minor == 1000


def test_revenue_event_rejects_naive_datetime():
    naive = datetime.now()  # noqa: DTZ005
    with pytest.raises(ValueError, match="timezone-aware"):
        RevenueEvent(
            event_id=RevenueEventId("evt_1"),
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(EventSourceType.INTERNAL),
            merchant_id=MerchantId("m_1"),
            occurred_at=naive,
            received_at=naive,
        )


def test_revenue_event_received_before_occurred():
    now = datetime.now(UTC)
    with pytest.raises(ValueError, match="received_at cannot precede occurred_at"):
        RevenueEvent(
            event_id=RevenueEventId("evt_1"),
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(EventSourceType.INTERNAL),
            merchant_id=MerchantId("m_1"),
            occurred_at=now,
            received_at=now - timedelta(minutes=1),
        )


def test_revenue_event_immutability():
    now = datetime.now(UTC)
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.INTERNAL),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )
    from dataclasses import FrozenInstanceError

    with pytest.raises(
        FrozenInstanceError
    ):  # Frozen dataclass raises FrozenInstanceError
        ev.event_type = RevenueEventType.PAYMENT_AUTHORIZED
