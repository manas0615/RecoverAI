import json
import logging
import urllib.error
import urllib.request
from datetime import UTC, datetime

from recoverai.config import settings
from recoverai.domain.action import ActionStatus, RecoveryAction
from recoverai.domain.audit import (
    AuditActor,
    AuditActorType,
    AuditEvent,
    AuditEventType,
)
from recoverai.domain.policy import PolicyDecisionValue
from recoverai.integrations.razorpay.adapter import RazorpayExecutionResultType
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.audit import AuditRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.policy.engine import PolicyEngine

logger = logging.getLogger(__name__)


class RecoveryActionService:
    def __init__(
        self,
        tm: TransactionManager,
        policy_engine: PolicyEngine,
        razorpay_adapter,
    ):
        self.tm = tm
        self.policy_engine = policy_engine
        self.razorpay_adapter = razorpay_adapter

    def execute_action(self, action: RecoveryAction) -> RecoveryAction:
        """
        The single authoritative financial execution path.
        """
        with self.tm.transaction() as conn:
            case_repo = RecoveryCaseRepository(conn)
            action_repo = RecoveryActionRepository(conn)
            audit_repo = AuditRepository(conn)

            from recoverai.integrations.razorpay.service import RazorpayExecutionService

            rzp_service = RazorpayExecutionService(self.razorpay_adapter, action_repo)

            case = case_repo.get(action.case_id)
            if not case:
                raise ValueError(f"Case {action.case_id} not found")

            from recoverai.policy.engine import PolicyContext

            policy_context = PolicyContext(
                policy_version="1.0", current_time=datetime.now(UTC)
            )

            if getattr(action, "_real_plan", None) is not None:
                plan = action._real_plan
            else:
                raise ValueError(
                    "Financial execution requires a real Intelligence InterventionPlan."
                )

            decision = self.policy_engine.evaluate(policy_context, case, plan, [])  # type: ignore

            # Audit policy decision
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.POLICY_DECISION_CREATED,
                    actor=AuditActor(type=AuditActorType.POLICY_ENGINE, id="policy"),
                    case_id=case.case_id,
                    action_id=action.action_id,
                    decision_reference=decision.policy_decision_id,
                    metadata={"decision": decision.decision.value},
                )
            )

            if decision.decision != PolicyDecisionValue.APPROVE:
                if decision.decision == PolicyDecisionValue.ESCALATE:
                    action.record_verification(
                        ActionStatus.ESCALATED, timestamp=datetime.now(UTC)
                    )
                    action_repo.save(action)
                    audit_repo.append(
                        AuditEvent(
                            event_type=AuditEventType.CASE_ESCALATED,
                            actor=AuditActor(type=AuditActorType.SYSTEM, id="policy"),
                            case_id=case.case_id,
                            action_id=action.action_id,
                        )
                    )
                    self._trigger_n8n(
                        "human-approval",
                        {
                            "case_id": case.case_id.value,
                            "action_id": action.action_id.value,
                        },
                    )
                else:
                    action.record_verification(
                        ActionStatus.CANCELLED, timestamp=datetime.now(UTC)
                    )
                    action_repo.save(action)
                return action

            # APPROVE Path
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.ACTION_AUTHORIZED,
                    actor=AuditActor(type=AuditActorType.SYSTEM, id="action_service"),
                    case_id=case.case_id,
                    action_id=action.action_id,
                    decision_reference=decision.policy_decision_id,
                )
            )

            action.status = ActionStatus.AUTHORIZED
            action_repo.save(action)

            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.ACTION_EXECUTING,
                    actor=AuditActor(type=AuditActorType.SYSTEM, id="action_service"),
                    case_id=case.case_id,
                    action_id=action.action_id,
                )
            )

            # Execute
            result = rzp_service.execute_and_record(action, case, decision)

            # Re-fetch action to get the updated status/reference
            fetched_action = action_repo.get(action.action_id)
            if fetched_action:
                action = fetched_action

            if result.result_type == RazorpayExecutionResultType.SUCCESSFUL_REQUEST:
                audit_repo.append(
                    AuditEvent(
                        event_type=AuditEventType.RAZORPAY_REQUEST_COMPLETED,
                        actor=AuditActor(type=AuditActorType.RAZORPAY, id="api"),
                        case_id=case.case_id,
                        action_id=action.action_id,
                        metadata={"provider_reference": result.provider_reference},
                    )
                )
                from recoverai.domain.case import CaseWorkflowState

                case.advance_workflow(CaseWorkflowState.VERIFYING, datetime.now(UTC))
                case_repo.save(case)
                # Orchestration handoff to n8n
                self._trigger_n8n(
                    "payment-recovery",
                    {
                        "case_id": case.case_id.value,
                        "action_id": action.action_id.value,
                    },
                )
                audit_repo.append(
                    AuditEvent(
                        event_type=AuditEventType.WORKFLOW_STARTED,
                        actor=AuditActor(
                            type=AuditActorType.SYSTEM, id="action_service"
                        ),
                        case_id=case.case_id,
                        action_id=action.action_id,
                    )
                )
            elif result.result_type in (
                RazorpayExecutionResultType.TIMEOUT_UNKNOWN,
                RazorpayExecutionResultType.NETWORK_UNKNOWN,
            ):
                audit_repo.append(
                    AuditEvent(
                        event_type=AuditEventType.ACTION_EXECUTION_UNKNOWN,
                        actor=AuditActor(type=AuditActorType.SYSTEM, id="transport"),
                        case_id=case.case_id,
                        action_id=action.action_id,
                        metadata={"error": result.error_message},
                    )
                )

            return action

    def _trigger_n8n(self, workflow_name: str, payload: dict):
        # We look up the webhook URL for the given workflow name or use a general n8n base url.
        n8n_url = settings.n8n_base_url
        if not n8n_url:
            return

        url = f"{n8n_url.rstrip('/')}/{workflow_name}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-N8N-API-Key": settings.n8n_api_key or "mock",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as _:
                pass
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to trigger n8n workflow {workflow_name}: {e}")
