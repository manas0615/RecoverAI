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


class CaseWorkflowState(Enum):
    DETECTED = "DETECTED"
    ENRICHING = "ENRICHING"
    ASSESSED = "ASSESSED"
    PLANNING = "PLANNING"
    POLICY_REVIEW = "POLICY_REVIEW"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    UNKNOWN = "UNKNOWN"
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
    workflow_state: CaseWorkflowState = field(default=CaseWorkflowState.DETECTED)
    outcome_type: RecoveryOutcomeValue | None = None
    version: int = 0
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
        if not isinstance(self.workflow_state, CaseWorkflowState):
            raise TypeError("workflow_state must be a CaseWorkflowState")
        if not isinstance(self.version, int) or self.version < 0:
            raise ValueError("version must be a non-negative integer")

        self._validate_state_invariants()

    def _validate_state_invariants(self) -> None:
        if self.status == RecoveryCaseStatus.CLOSED:
            if self.workflow_state != CaseWorkflowState.CLOSED:
                raise ValueError("A CLOSED case must have workflow_state=CLOSED")
            if self.outcome_type is None:
                raise ValueError("A CLOSED case must have an outcome_type")
        else:
            if self.workflow_state == CaseWorkflowState.CLOSED:
                raise ValueError("An OPEN case cannot have workflow_state=CLOSED")
            if self.outcome_type is not None:
                raise ValueError("An OPEN case cannot have an outcome_type")

    def add_source_event(self, event_id: RevenueEventId, timestamp: datetime) -> None:
        if self.status == RecoveryCaseStatus.CLOSED:
            raise ValueError("Cannot modify a closed RecoveryCase")
        if not isinstance(event_id, RevenueEventId):
            raise TypeError("event_id must be a RevenueEventId")
        self.source_event_ids.add(event_id)
        self.updated_at = timestamp

    def advance_workflow(
        self, new_state: CaseWorkflowState, timestamp: datetime
    ) -> None:
        """
        Advances the granular workflow state while the case is OPEN.
        """
        if self.status == RecoveryCaseStatus.CLOSED:
            raise ValueError("Cannot advance workflow of a CLOSED case")
        if new_state == CaseWorkflowState.CLOSED:
            raise ValueError(
                "Cannot transition to CLOSED via advance_workflow; use close()"
            )
        if not isinstance(new_state, CaseWorkflowState):
            raise TypeError("new_state must be a CaseWorkflowState")
        if not timestamp.tzinfo:
            raise ValueError("Timestamp must be timezone-aware")

        self.workflow_state = new_state
        self.updated_at = timestamp

    def close(
        self,
        outcome: RecoveryOutcomeValue,
        timestamp: datetime,
        recovered_amount: RevenueAmount | None = None,
    ) -> None:
        """
        Terminal state transition.
        """
        if self.status == RecoveryCaseStatus.CLOSED:
            raise ValueError("RecoveryCase is already closed")
        if not timestamp.tzinfo:
            raise ValueError("Timestamp must be timezone-aware")
        if not isinstance(outcome, RecoveryOutcomeValue):
            raise TypeError("outcome must be a RecoveryOutcomeValue")

        if outcome == RecoveryOutcomeValue.RECOVERED and recovered_amount is None:
            raise ValueError("RECOVERED outcome requires a recovered_amount")

        self.status = RecoveryCaseStatus.CLOSED
        self.workflow_state = CaseWorkflowState.CLOSED
        self.outcome_type = outcome
        self.recovered_amount = recovered_amount
        self.closed_at = timestamp
        self.updated_at = timestamp
