import logging
import uuid
from datetime import UTC, datetime

from recoverai.domain import (
    CurrencyCode,
    CustomerId,
    EventSource,
    EventSourceType,
    MerchantId,
    Money,
    RevenueEvent,
    RevenueEventId,
    RevenueEventType,
)
from recoverai.ingestion.exceptions import (
    MalformedWebhookPayload,
    UnsupportedWebhookEvent,
)

logger = logging.getLogger(__name__)

EVENT_TYPE_MAPPING = {
    "payment.authorized": RevenueEventType.PAYMENT_AUTHORIZED,
    "payment.captured": RevenueEventType.PAYMENT_CAPTURED,
    "payment.failed": RevenueEventType.PAYMENT_FAILED,
    "payment_link.paid": RevenueEventType.PAYMENT_LINK_PAID,
    "payment.downtime.started": RevenueEventType.PAYMENT_DEGRADATION_SIGNAL,
    "payment.downtime.updated": RevenueEventType.PAYMENT_DEGRADATION_SIGNAL,
}


class RazorpayNormalizer:
    """
    Normalizes Razorpay JSON into explicit pure-Python domain objects.
    Does NOT contain database logic.
    """

    def normalize(
        self,
        merchant_id: MerchantId,
        payload: dict,
        source_event_id: str | None,
        received_at: datetime,
    ) -> RevenueEvent:
        if not isinstance(payload, dict):
            raise MalformedWebhookPayload("Payload must be a dictionary")

        event_name = payload.get("event")
        if not event_name:
            raise MalformedWebhookPayload("Missing 'event' in envelope")

        if event_name not in EVENT_TYPE_MAPPING:
            raise UnsupportedWebhookEvent(f"Unsupported event type: {event_name}")

        event_type = EVENT_TYPE_MAPPING[event_name]

        try:
            contains = payload.get("contains", [])
            entity_type = contains[0] if contains else None

            primary_entity_data = None
            if "payload" in payload and isinstance(payload["payload"], dict):
                if entity_type and entity_type in payload["payload"]:
                    primary_entity_data = payload["payload"][entity_type].get(
                        "entity", {}
                    )
                else:
                    first_key = next(iter(payload["payload"].keys()), None)
                    if first_key:
                        primary_entity_data = payload["payload"][first_key].get(
                            "entity", {}
                        )

            if not primary_entity_data:
                primary_entity_data = {}

            external_reference = primary_entity_data.get("id")

            amount = None
            if "amount" in primary_entity_data and "currency" in primary_entity_data:
                amount = Money(
                    int(primary_entity_data["amount"]),
                    CurrencyCode(primary_entity_data["currency"]),
                )

            customer_id = None
            if primary_entity_data.get("customer_id"):
                customer_id = CustomerId(primary_entity_data["customer_id"])

            occurred_at = received_at
            if "created_at" in payload and isinstance(
                payload["created_at"], (int, float)
            ):
                occurred_at = datetime.fromtimestamp(payload["created_at"], tz=UTC)
            elif "created_at" in primary_entity_data and isinstance(
                primary_entity_data["created_at"], (int, float)
            ):
                occurred_at = datetime.fromtimestamp(
                    primary_entity_data["created_at"], tz=UTC
                )

            return RevenueEvent(
                event_id=RevenueEventId(str(uuid.uuid4())),
                event_type=event_type,
                source=EventSource(
                    source_type=EventSourceType.RAZORPAY_WEBHOOK,
                    source_event_id=source_event_id,
                ),
                merchant_id=merchant_id,
                customer_id=customer_id,
                amount=amount,
                external_reference=external_reference,
                metadata=payload,
                schema_version="1.0",
                occurred_at=occurred_at,
                received_at=received_at,
            )

        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise MalformedWebhookPayload(f"Failed to extract entity details: {e}")
            raise
