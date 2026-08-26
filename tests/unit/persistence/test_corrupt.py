from datetime import UTC, datetime

import pytest

from recoverai.domain import (
    EventSource,
    EventSourceType,
    MerchantId,
    RevenueEvent,
    RevenueEventId,
    RevenueEventType,
)
from recoverai.persistence.repositories.event import RevenueEventRepository


def test_corrupted_enum_fails_on_load(tm):
    now = datetime.now(UTC)
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_corr"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.INTERNAL),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )
    with tm.transaction() as conn:
        RevenueEventRepository(conn).save(ev)

    with tm.transaction() as conn:
        # Corrupt the enum in DB
        conn.execute(
            "UPDATE revenue_events SET event_type = 'INVALID_ENUM' WHERE event_id = 'evt_corr'"
        )

    with tm.transaction() as conn, pytest.raises(ValueError):
        RevenueEventRepository(conn).get(RevenueEventId("evt_corr"))


def test_naive_datetime_persisted_fails(tm):
    now = datetime.now(UTC)
    ev = RevenueEvent(
        event_id=RevenueEventId("evt_dt"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        source=EventSource(EventSourceType.INTERNAL),
        merchant_id=MerchantId("m_1"),
        occurred_at=now,
        received_at=now,
    )
    with tm.transaction() as conn:
        RevenueEventRepository(conn).save(ev)

    with tm.transaction() as conn:
        # Corrupt timestamp to naive
        conn.execute(
            "UPDATE revenue_events SET occurred_at = '2026-01-01T12:00:00' WHERE event_id = 'evt_dt'"
        )

    with tm.transaction() as conn, pytest.raises(ValueError, match="naive"):
        RevenueEventRepository(conn).get(RevenueEventId("evt_dt"))
