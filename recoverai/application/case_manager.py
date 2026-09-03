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

    def create_or_update_from_event(self, event: RevenueEvent) -> RecoveryCase | None:
        with self.tm.transaction() as conn:
            case_repo = RecoveryCaseRepository(conn)
            audit_repo = AuditRepository(conn)

            # Check if this is a failure on a recovery payment link (prevent loop)
            from recoverai.domain.event import RevenueEventType
            if event.event_type == RevenueEventType.PAYMENT_FAILED:
                metadata = event.metadata or {}
                payment_entity = metadata.get("payload", {}).get("payment", {}).get("entity", {})
                description = payment_entity.get("description") or ""
                
                plink_ref = None
                if description.startswith("#"):
                    plink_ref = f"plink_{description[1:]}"
                    
                if plink_ref:
                    from recoverai.persistence.repositories.action import RecoveryActionRepository
                    action_repo = RecoveryActionRepository(conn)
                    actions = action_repo.get_by_external_reference(plink_ref)
                    if actions:
                        from recoverai.domain.action import ActionStatus
                        from recoverai.domain.case import CaseWorkflowState
                        
                        found_case = None
                        for action in actions:
                            if action.status != ActionStatus.VERIFIED_FAILURE:
                                action.record_verification(ActionStatus.VERIFIED_FAILURE, event.occurred_at)
                                action_repo.save(action)
                                
                                audit_repo.append(
                                    AuditEvent(
                                        event_type=AuditEventType.VERIFICATION_COMPLETED,
                                        actor=AuditActor(type=AuditActorType.SYSTEM, id="case_manager"),
                                        case_id=action.case_id,
                                        action_id=action.action_id,
                                        timestamp=datetime.now(UTC),
                                        metadata={"verified_state": "FAILURE", "reason": "recovery_payment_failed"}
                                    )
                                )
                            
                            case = case_repo.get(action.case_id)
                            if case:
                                if case.workflow_state == CaseWorkflowState.VERIFYING:
                                    case.advance_workflow(CaseWorkflowState.PLANNING, event.occurred_at)
                                case.add_source_event(event.event_id, event.occurred_at)
                                case_repo.save(case)
                                found_case = case
                        
                        # We return the original case and do NOT create a new one
                        if found_case:
                            return found_case

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
