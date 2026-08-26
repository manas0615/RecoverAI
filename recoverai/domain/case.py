from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from recoverai.domain.identifiers import (
    CustomerId,
    MerchantId,
    RecoveryCaseId,
    RevenueEventId,
)
from recoverai.domain.money import RevenueAmount


class RecoveryCaseStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class RevenueSource(Enum):
    PAYMENT = "PAYMENT"
    CHECKOUT = "CHECKOUT"
    SUBSCRIPTION = "SUBSCRIPTION"
    RECEIVABLE = "RECEIVABLE"
    SYSTEMIC_PAYMENT_DEGRADATION = "SYSTEMIC_PAYMENT_DEGRADATION"


class RecoveryOutcomeValue(Enum):
    RECOVERED = "RECOVERED"
    NOT_RECOVERED = "NOT_RECOVERED"
    SUPPRESSED = "SUPPRESSED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


@dataclass
class RecoveryCase:
    """
    Central aggregate root representing a revenue opportunity.
    Mutable lifecycle object, but mutations should be controlled through domain methods.
    Does NOT own RevenueEvents, but associates with them via event IDs.
    """

    case_id: RecoveryCaseId
    merchant_id: MerchantId
    revenue_source: RevenueSource
    amount_at_risk: RevenueAmount
    opened_at: datetime

    # State fields
    source_event_ids: set[RevenueEventId]
    customer_id: CustomerId | None = None

    # Outcome fields
    status: RecoveryCaseStatus = field(default=RecoveryCaseStatus.OPEN)
    outcome_type: RecoveryOutcomeValue | None = None
    recovered_amount: RevenueAmount | None = None
    updated_at: datetime | None = None
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, RecoveryCaseId):
            raise TypeError("case_id must be a RecoveryCaseId")
        if not isinstance(self.merchant_id, MerchantId):
            raise TypeError("merchant_id must be a MerchantId")
        if not isinstance(self.revenue_source, RevenueSource):
            raise TypeError("revenue_source must be a RevenueSource")
        if not isinstance(self.amount_at_risk, RevenueAmount):
            raise TypeError("amount_at_risk must be a RevenueAmount")
        if not self.opened_at.tzinfo:
            raise ValueError("opened_at timestamp must be timezone-aware")
        if not self.source_event_ids:
            raise ValueError("A RecoveryCase must reference at least one source event")
        for eid in self.source_event_ids:
            if not isinstance(eid, RevenueEventId):
                raise TypeError("source_event_ids must contain only RevenueEventId")

    def add_source_event(self, event_id: RevenueEventId, timestamp: datetime) -> None:
        if self.status == RecoveryCaseStatus.CLOSED:
            raise ValueError("Cannot modify a closed RecoveryCase")
        if not isinstance(event_id, RevenueEventId):
            raise TypeError("event_id must be a RevenueEventId")
        self.source_event_ids.add(event_id)
        self.updated_at = timestamp

    def close(
        self,
        outcome: RecoveryOutcomeValue,
        timestamp: datetime,
        recovered_amount: RevenueAmount | None = None,
    ) -> None:
        """
        Terminal state transition. The exact conditions (e.g. requiring verification)
        will be enforced by the State Machine in P05, but we enforce basic intrinsic rules here.
        """
        if self.status == RecoveryCaseStatus.CLOSED:
            raise ValueError("RecoveryCase is already closed")
        if not timestamp.tzinfo:
            raise ValueError("Timestamp must be timezone-aware")
        if not isinstance(outcome, RecoveryOutcomeValue):
            raise TypeError("outcome must be a RecoveryOutcomeValue")

        # Intrinsic rule: RECOVERED must have a recovered_amount (verified amount).
        # The architecture says: "recovered_amount is determined from verified financial state."
        # The full requirement that verification exists is a P05 workflow rule,
        # but intrinsically RECOVERED implies a recovered amount.
        if outcome == RecoveryOutcomeValue.RECOVERED and recovered_amount is None:
            raise ValueError("RECOVERED outcome requires a recovered_amount")

        self.status = RecoveryCaseStatus.CLOSED
        self.outcome_type = outcome
        self.recovered_amount = recovered_amount
        self.closed_at = timestamp
        self.updated_at = timestamp
