import json
import sqlite3

from recoverai.domain import (
    CustomerId,
    EventSource,
    EventSourceType,
    MerchantId,
    RevenueEvent,
    RevenueEventId,
    RevenueEventType,
)
from recoverai.persistence.exceptions import DuplicateEntityError
from recoverai.persistence.mappers import (
    dt_to_str,
    row_to_money,
    safe_json_loads,
    str_to_dt,
)


class RevenueEventRepository:
    """
    Repository for RevenueEvent.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, event: RevenueEvent) -> None:
        """
        Inserts a new RevenueEvent. RevenueEvents are immutable, so we only insert.
        """
        amount_minor = event.amount.amount_minor if event.amount else None
        currency = event.amount.currency.value if event.amount else None

        try:
            self.conn.execute(
                """
                INSERT INTO revenue_events (
                    event_id, event_type, source_type, source_event_id,
                    merchant_id, customer_id, amount_minor, currency,
                    external_reference, metadata, schema_version,
                    occurred_at, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event.event_id.value,
                    event.event_type.value,
                    event.source.source_type.value,
                    event.source.source_event_id,
                    event.merchant_id.value,
                    event.customer_id.value if event.customer_id else None,
                    amount_minor,
                    currency,
                    event.external_reference,
                    json.dumps(event.metadata),
                    event.schema_version,
                    dt_to_str(event.occurred_at),
                    dt_to_str(event.received_at),
                ),
            )
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateEntityError(f"Duplicate event: {e}")
            raise

    def get(self, event_id: RevenueEventId) -> RevenueEvent | None:
        cur = self.conn.execute(
            "SELECT * FROM revenue_events WHERE event_id = ?", (event_id.value,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return self._map_row(row)

    def _map_row(self, row: dict) -> RevenueEvent:
        return RevenueEvent(
            event_id=RevenueEventId(row["event_id"]),
            event_type=RevenueEventType(row["event_type"]),
            source=EventSource(
                source_type=EventSourceType(row["source_type"]),
                source_event_id=row["source_event_id"],
            ),
            merchant_id=MerchantId(row["merchant_id"]),
            customer_id=CustomerId(row["customer_id"]) if row["customer_id"] else None,
            occurred_at=str_to_dt(row["occurred_at"]),  # type: ignore
            received_at=str_to_dt(row["received_at"]),  # type: ignore
            amount=row_to_money(row["amount_minor"], row["currency"]),
            external_reference=row["external_reference"],
            metadata=safe_json_loads(row["metadata"]) or {},  # type: ignore
            schema_version=row["schema_version"],
        )
