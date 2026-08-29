import logging
from datetime import UTC, datetime

from recoverai.domain.audit import (
    AuditActor,
    AuditActorType,
    AuditEvent,
    AuditEventType,
)
from recoverai.domain.case import (
    RecoveryCase,
    RevenueSource,
)
from recoverai.domain.event import RevenueEvent
from recoverai.domain.identifiers import RecoveryCaseId
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.audit import AuditRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository

logger = logging.getLogger(__name__)


class RecoveryCaseManager:
    def __init__(self, tm: TransactionManager):
        self.tm = tm

    def create_or_update_from_event(self, event: RevenueEvent) -> RecoveryCase:
        with self.tm.transaction() as conn:
            case_repo = RecoveryCaseRepository(conn)
            audit_repo = AuditRepository(conn)

            # Check if this event is already processed
            cur = conn.execute(
                "SELECT case_id FROM case_source_events WHERE event_id = ?",
                (event.event_id.value,),
            )
            row = cur.fetchone()
            if row:
                existing_case = case_repo.get(RecoveryCaseId(row["case_id"]))
                if existing_case:
                    return existing_case

            # Check if there is already an open case for this source_event_id (payment_id)
            case_id_value = (
                f"case_{event.source.source_event_id or event.event_id.value}"
            )
            case_id = RecoveryCaseId(case_id_value)

            existing = case_repo.get(case_id)
            if existing:
                existing.add_source_event(event.event_id, event.received_at)
                case_repo.save(existing)
                return existing

            from recoverai.domain.money import RevenueAmount

            if not event.amount:
                raise ValueError("Event amount is required for case creation")

            case = RecoveryCase(
                case_id=case_id,
                merchant_id=event.merchant_id,
                revenue_source=RevenueSource.PAYMENT,
                amount_at_risk=RevenueAmount(event.amount),
                opened_at=event.occurred_at,
                source_event_ids={event.event_id},
                customer_id=event.customer_id,
            )
            case_repo.save(case)

            audit_event = AuditEvent(
                event_type=AuditEventType.CASE_CREATED,
                actor=AuditActor(type=AuditActorType.SYSTEM, id="case_manager"),
                case_id=case.case_id,
                timestamp=datetime.now(UTC),
                metadata={
                    "event_id": event.event_id.value,
                    "amount_minor": event.amount.amount_minor,
                },
            )
            audit_repo.append(audit_event)

            return case
