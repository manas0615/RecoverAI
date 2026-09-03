import uuid
from datetime import datetime

from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction
from recoverai.domain.audit import (
    AuditActor,
    AuditActorType,
    AuditEvent,
    AuditEventType,
)
from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCase,
    RecoveryOutcomeValue,
)
from recoverai.domain.event import RevenueEventType
from recoverai.domain.evidence import EvidenceReference, EvidenceSourceType
from recoverai.domain.identifiers import VerificationRecordId
from recoverai.domain.verification import (
    VerificationRecord,
    VerificationSource,
    VerifiedState,
)
from recoverai.integrations.razorpay.parser import RazorpayEventParser
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.audit import AuditRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository
from recoverai.persistence.repositories.verification import (
    VerificationRecordRepository,
)


class VerificationEngine:
    def __init__(
        self,
        action_repo: RecoveryActionRepository,
        case_repo: RecoveryCaseRepository,
        event_repo: RevenueEventRepository,
        verification_repo: VerificationRecordRepository,
        audit_repo: "AuditRepository | None" = None,
    ):
        self.action_repo = action_repo
        self.case_repo = case_repo
        self.event_repo = event_repo
        self.verification_repo = verification_repo
        self.audit_repo = audit_repo

    def reconcile_case(self, case: RecoveryCase, current_time: datetime) -> None:
        """
        Reconciles a case by verifying its pending actions.
        """
        if case.workflow_state not in (
            CaseWorkflowState.VERIFYING,
            CaseWorkflowState.UNKNOWN,
        ):
            return

        actions = self.action_repo.get_pending_verification(case.case_id)
        for action in actions:
            record = self._verify_action(action, case, current_time)
            if record:
                self.verification_repo.save(record)

                # Apply action status
                if record.verified_state == VerifiedState.SUCCESS:
                    action.record_verification(
                        ActionStatus.VERIFIED_SUCCESS, current_time
                    )
                elif record.verified_state == VerifiedState.FAILURE:
                    action.record_verification(
                        ActionStatus.VERIFIED_FAILURE, current_time
                    )
                elif record.verified_state == VerifiedState.UNKNOWN:
                    pass  # stays in EXECUTION_UNKNOWN or VERIFICATION_PENDING

                self.action_repo.save(action)

                if self.audit_repo:
                    self.audit_repo.append(
                        AuditEvent(
                            event_type=AuditEventType.VERIFICATION_COMPLETED,
                            actor=AuditActor(
                                type=AuditActorType.SYSTEM, id="verification_engine"
                            ),
                            case_id=case.case_id,
                            action_id=action.action_id,
                            metadata={"verified_state": record.verified_state.value},
                        )
                    )

        # After checking all actions, see if we can transition the case
        # If any action was VERIFIED_SUCCESS, the case is RECOVERED.
        # Note: We must fetch the latest state of actions
        updated_actions = self.action_repo.get_by_case(case.case_id)

        has_success = any(
            a.status == ActionStatus.VERIFIED_SUCCESS for a in updated_actions
        )

        if has_success:
            # We need to find the successful event to get the recovered amount.
            # For simplicity in this implementation, we take the case's amount_at_risk if it was fully recovered.
            case.close(
                RecoveryOutcomeValue.RECOVERED,
                current_time,
                recovered_amount=case.amount_at_risk,
            )
            self.case_repo.save(case)
            return

        # If all actions are VERIFIED_FAILURE, the case might go to NOT_RECOVERED,
        # but that depends on policy/retry eligibility, so we can leave it to the state machine / workflow orchestrator,
        # or we set it to PLANNING to try again.
        # For P09, if it's VERIFIED_FAILURE, we just update the case workflow state to PLANNING.
        all_failed = all(
            a.status in (ActionStatus.VERIFIED_FAILURE, ActionStatus.CANCELLED)
            for a in updated_actions
        )
        if all_failed and case.workflow_state == CaseWorkflowState.VERIFYING:
            case.advance_workflow(CaseWorkflowState.PLANNING, current_time)
            self.case_repo.save(case)

    def _verify_action(
        self, action: RecoveryAction, case: RecoveryCase, current_time: datetime
    ) -> VerificationRecord | None:
        if action.status not in (
            ActionStatus.VERIFICATION_PENDING,
            ActionStatus.EXECUTION_UNKNOWN,
        ):
            return None

        if action.action_type == ActionType.CREATE_PAYMENT_LINK:
            return self._verify_payment_link(action, case, current_time)

        return None

    def _verify_payment_link(
        self, action: RecoveryAction, case: RecoveryCase, current_time: datetime
    ) -> VerificationRecord | None:
        # 1. If provider synchronously rejected, it's a failure (no external reference).
        if (
            action.status == ActionStatus.VERIFICATION_PENDING
            and action.external_reference is None
            and action.failure_reason
        ):
            return VerificationRecord(
                verification_id=VerificationRecordId(f"vr_{uuid.uuid4().hex}"),
                action_id=action.action_id,
                case_id=case.case_id,
                verification_source=VerificationSource.RAZORPAY_API,
                verified_state=VerifiedState.FAILURE,
                checked_at=current_time,
            )

        # 2. Look for PAYMENT_LINK_PAID event
        matching_event = None

        if action.external_reference:
            events = self.event_repo.get_by_external_reference(
                action.external_reference
            )
            for event in events:
                if event.event_type == RevenueEventType.PAYMENT_LINK_PAID:
                    matching_event = event
                    break
        else:
            # EXECUTION_UNKNOWN, need to match by idempotency_key (reference_id)
            if not action.idempotency_key:
                return None

            events = self.event_repo.get_by_merchant_and_type(
                case.merchant_id, RevenueEventType.PAYMENT_LINK_PAID
            )
            for event in events:
                ref_id = RazorpayEventParser.extract_reference_id(event)
                if ref_id == action.idempotency_key:
                    matching_event = event
                    break

        if not matching_event:
            # No evidence found, remains in current state
            return None

        # 3. We found a PAYMENT_LINK_PAID event. Now verify amount and currency.
        if not matching_event.amount:
            return VerificationRecord(
                verification_id=VerificationRecordId(f"vr_{uuid.uuid4().hex}"),
                action_id=action.action_id,
                case_id=case.case_id,
                verification_source=VerificationSource.PAYMENT_LINK_WEBHOOK,
                verified_state=VerifiedState.UNKNOWN,
                checked_at=current_time,
                external_reference=matching_event.external_reference,
                evidence_reference=EvidenceReference(
                    source_type=EvidenceSourceType.RAZORPAY_EVENT,
                    source_id=matching_event.event_id.value,
                    observed_at=matching_event.occurred_at,
                ),
            )
            
        if matching_event.amount.currency != case.amount_at_risk.currency:
            # Currency mismatch - safe failure / escalate
            return VerificationRecord(
                verification_id=VerificationRecordId(f"vr_{uuid.uuid4().hex}"),
                action_id=action.action_id,
                case_id=case.case_id,
                verification_source=VerificationSource.PAYMENT_LINK_WEBHOOK,
                verified_state=VerifiedState.UNKNOWN,
                checked_at=current_time,
                external_reference=matching_event.external_reference,
                evidence_reference=EvidenceReference(
                    source_type=EvidenceSourceType.RAZORPAY_EVENT,
                    source_id=matching_event.event_id.value,
                    observed_at=matching_event.occurred_at,
                ),
            )
        if matching_event.amount.amount_minor != case.amount_at_risk.amount_minor:
            # Amount mismatch - safe failure / escalate
            return VerificationRecord(
                verification_id=VerificationRecordId(f"vr_{uuid.uuid4().hex}"),
                action_id=action.action_id,
                case_id=case.case_id,
                verification_source=VerificationSource.PAYMENT_LINK_WEBHOOK,
                verified_state=VerifiedState.UNKNOWN,
                checked_at=current_time,
                external_reference=matching_event.external_reference,
                evidence_reference=EvidenceReference(
                    source_type=EvidenceSourceType.RAZORPAY_EVENT,
                    source_id=matching_event.event_id.value,
                    observed_at=matching_event.occurred_at,
                ),
            )

        return VerificationRecord(
            verification_id=VerificationRecordId(f"vr_{uuid.uuid4().hex}"),
            action_id=action.action_id,
            case_id=case.case_id,
            verification_source=VerificationSource.PAYMENT_LINK_WEBHOOK,
            verified_state=VerifiedState.SUCCESS,
            checked_at=current_time,
            external_reference=matching_event.external_reference,
            evidence_reference=EvidenceReference(
                source_type=EvidenceSourceType.RAZORPAY_EVENT,
                source_id=matching_event.event_id.value,
                observed_at=matching_event.occurred_at,
            ),
        )
