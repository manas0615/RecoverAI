from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from recoverai.domain.identifiers import CustomerId, MerchantId, RevenueEventId
from recoverai.domain.money import Money


class RevenueEventType(Enum):
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    PAYMENT_CAPTURED = "PAYMENT_CAPTURED"
    PAYMENT_LINK_PAID = "PAYMENT_LINK_PAID"
    ORDER_PAID = "ORDER_PAID"
    CHECKOUT_STARTED = "CHECKOUT_STARTED"
    CHECKOUT_ABANDONED = "CHECKOUT_ABANDONED"
    SUBSCRIPTION_PAYMENT_FAILED = "SUBSCRIPTION_PAYMENT_FAILED"
    RECEIVABLE_OVERDUE = "RECEIVABLE_OVERDUE"
    PAYMENT_DEGRADATION_SIGNAL = "PAYMENT_DEGRADATION_SIGNAL"


class EventSourceType(Enum):
    RAZORPAY_WEBHOOK = "RAZORPAY_WEBHOOK"
    SIMULATION = "SIMULATION"
    INTERNAL = "INTERNAL"


@dataclass(frozen=True)
class EventSource:
    source_type: EventSourceType
    source_event_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_type, EventSourceType):
            raise TypeError("source_type must be an EventSourceType")


@dataclass(frozen=True)
class RevenueEvent:
    """
    Represents an observed external or synthetic revenue-related event.
    Immutable historical fact. Does NOT require a RecoveryCase to exist.
    """

    event_id: RevenueEventId
    event_type: RevenueEventType
    source: EventSource
    merchant_id: MerchantId
    occurred_at: datetime
    received_at: datetime
    customer_id: CustomerId | None = None
    amount: Money | None = None
    external_reference: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, RevenueEventId):
            raise TypeError("event_id must be a RevenueEventId")
        if not isinstance(self.event_type, RevenueEventType):
            raise TypeError("event_type must be a RevenueEventType")
        if not isinstance(self.source, EventSource):
            raise TypeError("source must be an EventSource")
        if not isinstance(self.merchant_id, MerchantId):
            raise TypeError("merchant_id must be a MerchantId")
        if not self.occurred_at.tzinfo or not self.received_at.tzinfo:
            raise ValueError("Timestamps must be timezone-aware")
        if self.received_at < self.occurred_at:
            raise ValueError("received_at cannot precede occurred_at")
        if self.amount is not None and not isinstance(self.amount, Money):
            raise TypeError("amount must be a Money object")
