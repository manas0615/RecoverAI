import os
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recoverai.api.security import require_frontend_key, require_n8n_key
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId
from recoverai.ingestion.exceptions import DuplicateWebhookEvent, EventIngestionError
from recoverai.ingestion.razorpay.normalizer import RazorpayNormalizer
from recoverai.ingestion.razorpay.service import WebhookIngestionService
from recoverai.ingestion.razorpay.signature import WebhookVerifier
from recoverai.integrations.razorpay.adapter import RazorpayAdapter, RazorpayConfig
from recoverai.integrations.razorpay.service import RazorpayExecutionService
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from recoverai.mcp.context import MCPContext
from recoverai.mcp.server import create_mcp_registry
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.persistence.repositories.audit import AuditRepository
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.persistence.repositories.event import RevenueEventRepository
from recoverai.persistence.repositories.verification import VerificationRecordRepository
from recoverai.policy.engine import PolicyEngine
from recoverai.state_machine.engine import RecoveryStateMachine
from recoverai.verification.engine import VerificationEngine


class AppContainer:
    def __init__(self):
        from recoverai.config import settings

        self.tm = TransactionManager(settings.database_url)

        # Keep global connection open first so the DB is not destroyed if it is an in-memory DB
        self.global_conn = self.tm.create_connection()

        migrations_dir = (
            Path(os.path.dirname(__file__)).parent / "persistence" / "migrations"
        )
        self.tm.run_migrations(migrations_dir)

        action_repo = RecoveryActionRepository(self.global_conn)
        case_repo = RecoveryCaseRepository(self.global_conn)
        event_repo = RevenueEventRepository(self.global_conn)
        verification_repo = VerificationRecordRepository(self.global_conn)
        audit_repo = AuditRepository(self.global_conn)

        self.policy = PolicyEngine(lambda: f"dec_{uuid.uuid4().hex[:8]}")
        self.llm = ConcreteLLMGateway(GatewayConfig.from_env())

        rzp_config = RazorpayConfig(
            key_id=settings.razorpay_key_id or "mock",
            key_secret=settings.razorpay_key_secret or "mock",
            mode=settings.razorpay_mode,
        )
        self.rzp_adapter = RazorpayAdapter(rzp_config)
        self.rzp_service = RazorpayExecutionService(self.rzp_adapter, action_repo)

        self.verification = VerificationEngine(
            action_repo=action_repo,
            case_repo=case_repo,
            event_repo=event_repo,
            verification_repo=verification_repo,
            audit_repo=audit_repo,
        )

        from recoverai.application.action_service import RecoveryActionService
        from recoverai.application.case_manager import RecoveryCaseManager
        from recoverai.intelligence.analyzer import RevenueIntelligenceAnalyzer

        self.action_service = RecoveryActionService(
            tm=self.tm, policy_engine=self.policy, razorpay_adapter=self.rzp_adapter
        )
        self.intelligence = RevenueIntelligenceAnalyzer(self.llm)
        self.case_manager = RecoveryCaseManager(self.tm)

        self.mcp_context = MCPContext(
            tm=self.tm,
            policy_engine=self.policy,
            razorpay_service=self.rzp_service,
            state_machine=RecoveryStateMachine(self.tm),
            action_service=self.action_service,
            intelligence=self.intelligence,
        )
        self.mcp_registry = create_mcp_registry(self.mcp_context)

        self.verifier = WebhookVerifier(settings.razorpay_webhook_secret or "secret")
        self.normalizer = RazorpayNormalizer()
        self.ingestion = WebhookIngestionService(
            self.verifier, self.normalizer, self.tm
        )

    def close(self):
        self.global_conn.close()


container = AppContainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup reconciliation
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.case import RecoveryCaseRepository
        from recoverai.persistence.repositories.event import RevenueEventRepository

        action_repo = RecoveryActionRepository(conn)
        case_repo = RecoveryCaseRepository(conn)
        event_repo = RevenueEventRepository(conn)

        # 1. Verify pending actions
        actions = action_repo.get_all_pending_verification()
        cases_to_verify = {a.case_id for a in actions}
        for cid in cases_to_verify:
            case = case_repo.get(cid)
            if case:
                container.verification.reconcile_case(case, datetime.now(UTC))
                container.global_conn.commit()

        # 2. Process unprocessed events
        unprocessed = event_repo.get_unprocessed_events()
        for event in unprocessed:
            if event.event_type.value == "PAYMENT_FAILED":
                try:
                    container.case_manager.create_or_update_from_event(event)
                    container.global_conn.commit()
                except Exception as e:  # noqa: BLE001  # noqa: BLE001  # noqa: BLE001
                    import logging

                    logging.getLogger(__name__).error(
                        f"Failed to process event {event.event_id}: {e}"
                    )

    yield
    container.close()


app = FastAPI(title="RecoverAI", lifespan=lifespan)

from recoverai.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


class MCPExecuteRequest(BaseModel):
    tool: str
    args: dict[str, Any]


@app.post("/mcp/execute", dependencies=[Depends(require_n8n_key)])
def execute_mcp_tool(req: MCPExecuteRequest):
    result = container.mcp_registry.execute(req.tool, req.args)
    if "error" in result and result.get("code") == "UNKNOWN_TOOL":
        raise HTTPException(status_code=400, detail=result["error"])
    return result


def case_to_dict(case) -> dict:
    return {
        "case_id": str(case.case_id.value),
        "merchant_id": str(case.merchant_id.value),
        "customer_id": str(case.customer_id.value) if case.customer_id else None,
        "status": case.status.value,
        "created_at": case.opened_at.isoformat(),
        "amount_minor": case.amount_at_risk.amount_minor,
        "currency": case.amount_at_risk.currency.value,
        "verification_count": 0,
        "workflow_state": case.workflow_state.value,
        "outcome_type": case.outcome_type.value if case.outcome_type else None,
        "recovered_amount_minor": case.recovered_amount.amount_minor
        if case.recovered_amount
        else None,
    }


@app.get("/recovery-cases", dependencies=[Depends(require_frontend_key)])
def list_cases():
    with container.tm.transaction() as conn:
        cur = conn.execute("SELECT case_id FROM recovery_cases ORDER BY opened_at DESC")
        repo = RecoveryCaseRepository(conn)

        # We need failure codes and recommendations
        cases = []
        for row in cur.fetchall():
            case_id_val = row["case_id"]
            c = repo.get(RecoveryCaseId(case_id_val))
            if c:
                d = case_to_dict(c)

                # Fetch failure code from events
                d["failure_code"] = "UNKNOWN"
                from recoverai.persistence.repositories.event import (
                    RevenueEventRepository,
                )

                event_repo = RevenueEventRepository(conn)

                events = [event_repo.get(eid) for eid in c.source_event_ids]
                for e in events:
                    if e and e.metadata.get("error_code"):
                        d["failure_code"] = e.metadata["error_code"]
                        break
                    if e and e.metadata.get("failure_reason"):
                        d["failure_code"] = e.metadata["failure_reason"]
                        break

                # Fetch recommendation from audit log
                d["recommendation"] = "N/A"
                from recoverai.persistence.repositories.audit import AuditRepository

                audit_repo = AuditRepository(conn)
                audit_events = audit_repo.get_by_case(case_id_val)
                for ae in audit_events:
                    if (
                        ae.event_type.value == "LLM_RECOMMENDATION_CREATED"
                        and ae.metadata
                        and "recommended_action" in ae.metadata
                    ):
                        d["recommendation"] = ae.metadata["recommended_action"]

                # Determine updated_at
                updated_at = c.updated_at or c.opened_at
                d["updated_at"] = updated_at.isoformat()

                # Fetch latest action details for execution monitoring
                from recoverai.persistence.repositories.action import (
                    RecoveryActionRepository,
                )

                action_repo = RecoveryActionRepository(conn)
                actions = action_repo.get_by_case(RecoveryCaseId(case_id_val))
                if actions:
                    latest_action = max(actions, key=lambda x: x.requested_at)
                    d["action_type"] = latest_action.action_type.value
                    d["action_status"] = latest_action.status.value
                    d["action_id"] = latest_action.action_id.value
                    d["provider"] = getattr(latest_action, "provider", None)
                    d["external_reference"] = getattr(latest_action, "external_reference", None)
                    d["workflow_execution_reference"] = getattr(latest_action, "workflow_execution_reference", None)
                else:
                    d["action_type"] = None
                    d["action_status"] = None
                    d["action_id"] = None
                    d["provider"] = None
                    d["external_reference"] = None
                    d["workflow_execution_reference"] = None

                cases.append(d)

        return {"cases": cases}


@app.get("/recovery-cases/{case_id}", dependencies=[Depends(require_frontend_key)])
def get_case(case_id: str):
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.audit import AuditRepository
        from recoverai.persistence.repositories.event import RevenueEventRepository

        repo = RecoveryCaseRepository(conn)
        event_repo = RevenueEventRepository(conn)
        audit_repo = AuditRepository(conn)

        try:
            case = repo.get(RecoveryCaseId(case_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid case ID")
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")




        events = [event_repo.get(eid) for eid in case.source_event_ids]

        audit_events = audit_repo.get_by_case(case_id)
        result = case_to_dict(case)
        result["timeline"] = [e.to_dict() for e in audit_events]
        result["events"] = [
            {
                "event_id": e.event_id.value,
                "event_type": e.event_type.value,
                "amount_minor": e.amount.amount_minor if e.amount else None,
                "currency": e.amount.currency.value if e.amount else None,
                "occurred_at": e.occurred_at.isoformat(),
                "external_reference": e.external_reference,
                "metadata": e.metadata,
            }
            for e in events
            if e
        ]

        # Gather evidence
        result["failure_code"] = "UNKNOWN"
        result["historical_failure_count"] = len(
            [e for e in events if e and "FAIL" in e.event_type.value]
        )
        for e in events:
            if e and e.metadata.get("error_code"):
                result["failure_code"] = e.metadata["error_code"]
                break
            if e and e.metadata.get("failure_reason"):
                result["failure_code"] = e.metadata["failure_reason"]
                break

        # Gather Recommendation
        result["recommendation"] = "N/A"
        result["confidence"] = None
        result["reasoning"] = None
        result["provenance"] = None

        audit_events = audit_repo.get_by_case(case_id)
        for ae in audit_events:
            if ae.event_type.value == "LLM_RECOMMENDATION_CREATED" and ae.metadata:
                if "recommended_action" in ae.metadata:
                    result["recommendation"] = ae.metadata["recommended_action"]
                if "confidence" in ae.metadata:
                    result["confidence"] = ae.metadata["confidence"]
                if "reasoning" in ae.metadata:
                    result["reasoning"] = ae.metadata["reasoning"]

                # Provenance
                actor_id = ae.actor.id if ae.actor else "UNKNOWN"
                if "gemini" in actor_id.lower() or "gemini" in str(ae.metadata).lower():
                    result["provenance"] = "Gemini"
                else:
                    result["provenance"] = "Deterministic Fallback"

            if (
                ae.event_type.value
                in ("POLICY_DECISION_CREATED", "POLICY_DECISION_RECORDED")
                and ae.metadata
            ):
                result["policy_decision"] = ae.metadata.get("decision")
                result["policy_reasons"] = ae.metadata.get("reasons", [])

        # Find action details and verification details for execution & verification UI
        try:
            from recoverai.persistence.repositories.action import (
                RecoveryActionRepository,
            )
            from recoverai.persistence.repositories.verification import (
                VerificationRecordRepository,
            )

            action_repo = RecoveryActionRepository(conn)
            ver_repo = VerificationRecordRepository(conn)

            actions = action_repo.get_by_case(RecoveryCaseId(case_id))
            if actions:
                latest_action = max(actions, key=lambda x: x.requested_at)
                result["action_type"] = latest_action.action_type.value
                result["action_status"] = latest_action.status.value
                result["action_id"] = latest_action.action_id.value
                result["provider"] = getattr(latest_action, "provider", None)
                result["external_reference"] = getattr(latest_action, "external_reference", None)
                result["workflow_execution_reference"] = getattr(latest_action, "workflow_execution_reference", None)
                result["action_requested_at"] = (
                    latest_action.requested_at.isoformat()
                    if latest_action.requested_at
                    else None
                )
                result["action_executed_at"] = (
                    latest_action.started_at.isoformat()
                    if latest_action.started_at
                    else None
                )

                # Verification Details
                records = ver_repo.get_by_case(RecoveryCaseId(case_id))
                if records:
                    latest_record = records[0]
                    result["verification_state"] = latest_record.verified_state.value
                    result["verification_source"] = (
                        latest_record.verification_source.value
                    )
                    result["verification_checked_at"] = (
                        latest_record.checked_at.isoformat()
                    )

                    # Gather observed evidence details if available
                    if latest_action.external_reference:
                        events = event_repo.get_by_external_reference(  # type: ignore
                            latest_action.external_reference
                        )
                        for ev in events:
                            if ev.event_type.value == "PAYMENT_LINK_PAID":  # type: ignore
                                result["observed_event_type"] = ev.event_type.value  # type: ignore
                                result["observed_amount_minor"] = (
                                    ev.amount.amount_minor if ev.amount else None  # type: ignore
                                )
                                result["observed_currency"] = (
                                    ev.amount.currency.value if ev.amount else None  # type: ignore
                                )
                                result["observed_reference"] = getattr(
                                    ev, "external_reference", None
                                )
                                break
                    elif getattr(latest_action, "idempotency_key", None):
                        events = event_repo.get_by_merchant_and_type(  # type: ignore
                            case.merchant_id,
                            "PAYMENT_LINK_PAID",  # type: ignore
                        )
                        for ev in events:
                            # Mock extract ref
                            result["observed_event_type"] = ev.event_type.value  # type: ignore
                            result["observed_amount_minor"] = (
                                ev.amount.amount_minor if ev.amount else None  # type: ignore
                            )
                            result["observed_currency"] = (
                                ev.amount.currency.value if ev.amount else None  # type: ignore
                            )
                            result["observed_reference"] = getattr(
                                ev, "external_reference", None
                            )
                            break

        except Exception as e:  # noqa: BLE001
            import logging

            logging.getLogger(__name__).warning(
                f"Failed to enrich case details for {case_id}: {e}"
            )

        return result


@app.get(
    "/recovery-cases/{case_id}/timeline", dependencies=[Depends(require_frontend_key)]
)
def get_case_timeline(case_id: str):
    with container.tm.transaction() as conn:
        repo = AuditRepository(conn)
        events = repo.get_by_case(case_id)
        return {"events": [e.to_dict() for e in events]}


@app.post(
    "/recovery-cases/{case_id}/analyze", dependencies=[Depends(require_frontend_key)]
)
async def analyze_case(case_id: str):
    with container.tm.transaction() as conn:
        case_repo = RecoveryCaseRepository(conn)
        event_repo = RevenueEventRepository(conn)
        try:
            case = case_repo.get(RecoveryCaseId(case_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid case ID")
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        if case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")




        events = [event_repo.get(eid) for eid in case.source_event_ids]

    try:
        from datetime import UTC, datetime

        from recoverai.domain.audit import (
            AuditActor,
            AuditActorType,
            AuditEvent,
            AuditEventType,
        )
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.audit import AuditRepository
        from recoverai.policy.engine import PolicyContext

        # 1. Start Analysis
        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.ANALYSIS_STARTED,
                    actor=AuditActor(type=AuditActorType.SYSTEM, id="api"),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                )
            )

        # 2. Run Intelligence (Outside transaction so frontend can poll)
        risk, cause, plan = container.intelligence.analyze(case, events)

        # 3. Commit LLM Recommendation
        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.LLM_RECOMMENDATION_CREATED,
                    actor=AuditActor(
                        type=AuditActorType.LLM_AGENT,
                        id=plan.selection_model_version if plan else "UNKNOWN",
                    ),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                    metadata={
                        "recommended_action": plan.selected_action_type.value
                        if plan and plan.selected_action_type
                        else "UNKNOWN",
                        "reasoning": plan.selection_reason
                        if plan
                        else "Analysis completed without forming an intervention plan.",
                        "confidence": (
                            next(
                                (
                                    c.expected_recovery_probability.value
                                    for c in plan.candidates
                                    if c.action_type == plan.selected_action_type
                                ),
                                None,
                            )
                            if plan
                            else None
                        ),
                        "cause_category": cause.category if cause else None,
                        "recovery_probability": risk.recovery_probability.value
                        if risk
                        else 0.0,
                        "expected_recovery_amount": plan.expected_recovery_value.amount_minor
                        if plan and plan.expected_recovery_value
                        else (
                            risk.expected_recovery_value.amount_minor
                            if risk and risk.expected_recovery_value
                            else 0
                        ),
                        "expected_recovery_currency": plan.expected_recovery_value.currency.value
                        if plan and plan.expected_recovery_value
                        else (
                            risk.expected_recovery_value.currency.value
                            if risk and risk.expected_recovery_value
                            else "INR"
                        ),
                        "analysis_source": "Gemini"
                        if (cause and cause.analysis_type.name == "LLM")
                        else "Deterministic Fallback",
                        "deterministic_fallback": cause.analysis_type.name != "LLM"
                        if cause
                        else True,
                        "probability_meaning": getattr(
                            risk.recovery_probability,
                            "reasoning",
                            "Derived from historical failure count and systemic signals",
                        )
                        if risk
                        else "No risk assessment available",
                        "model_version": plan.selection_model_version
                        if plan
                        else "UNKNOWN",
                    },
                )
            )

        # 4. Evaluate Policy
        policy_context = PolicyContext(
            policy_version="1.0", current_time=datetime.now(UTC)
        )
        with container.tm.transaction() as conn:
            action_history = RecoveryActionRepository(conn).get_by_case(case.case_id)

        decision = container.policy.evaluate(
            policy_context, case, plan, action_history, cause=cause
        )

        # 5. Commit Policy Decision
        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.POLICY_DECISION_CREATED,
                    actor=AuditActor(type=AuditActorType.POLICY_ENGINE, id="policy"),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                    metadata={
                        "decision": decision.decision.value,
                        "reasons": decision.reason_codes,
                        "decision_reason": ", ".join(decision.reason_codes),
                    },
                )
            )

        
        # 6. Auto-execute based on policy decision
        from recoverai.domain.action import ActionStatus, ActionType, RecoveryAction, RecoveryActionId
        import uuid
        
        with container.tm.transaction() as conn:
            action_repo = RecoveryActionRepository(conn)
            
            action = RecoveryAction(
                action_id=RecoveryActionId(f"act_{uuid.uuid4().hex[:12]}"),
                case_id=case.case_id,
                action_type=plan.selected_action_type if plan and plan.selected_action_type else ActionType.CREATE_PAYMENT_LINK,
                requested_at=datetime.now(UTC),
                status=ActionStatus.ESCALATED if decision.decision == PolicyDecisionValue.ESCALATE else (ActionStatus.PROPOSED if decision.decision == PolicyDecisionValue.APPROVE else ActionStatus.CANCELLED)
            )
            
            # Since action_service evaluates policy again and requires these:
            setattr(action, "_real_plan", plan)
            setattr(action, "_real_cause", cause)
            import json
            if plan:
                action.plan_snapshot = json.dumps(plan.to_dict())
            
            # Action repo doesn't persist _real_plan, so we execute immediately if APPROVE or ESCALATE
            # But wait, action MUST be in DB for action_service to claim_for_execution!
            # Let's save it to DB first.
            action_repo.save(action)
        
        # Now execute it if it's not denied
        if decision.decision in [PolicyDecisionValue.APPROVE, PolicyDecisionValue.ESCALATE]:
            # execute_action handles the policy check and status transitions!
            # We must set real_plan again because we just saved it and execute_action will need it
            setattr(action, "_real_plan", plan)
            setattr(action, "_real_cause", cause)
            import json
            if plan:
                action.plan_snapshot = json.dumps(plan.to_dict())
            try:
                container.action_service.execute_action(action)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Execution failed: {e}")
        
        return {

            "status": "success",
            "recommendation": plan.selected_action_type.value
            if plan and plan.selected_action_type
            else "UNKNOWN",
            "recommendation_reason": plan.selection_reason
            if plan
            else "Analysis completed without forming an intervention plan.",
            "expected_recovery_value": plan.expected_recovery_value.amount_minor
            if plan and plan.expected_recovery_value
            else (
                risk.expected_recovery_value.amount_minor
                if risk and risk.expected_recovery_value
                else 0
            ),
            "recovery_probability": risk.recovery_probability.value if risk else 0.0,
            "probability_meaning": getattr(
                risk.recovery_probability,
                "reasoning",
                "Derived from historical failure count and systemic signals",
            )
            if risk
            else "No risk assessment available",
            "cause_category": cause.category if cause else "UNKNOWN",
            "cause_confidence": cause.confidence.value if cause else 0.0,
            "policy_decision": decision.decision.value if decision else "UNKNOWN",
            "policy_reasons": decision.reason_codes if decision else [],
            "model_version": plan.selection_model_version if plan else "UNKNOWN",
        }
    except Exception as e:  # noqa: BLE001  # noqa: BLE001
        import logging

        logging.getLogger(__name__).error(f"Analysis failed for {case_id}: {e}")
        raise HTTPException(status_code=500, detail="Analysis unavailable")


@app.post("/webhooks/razorpay/{merchant_id}")
async def razorpay_webhook(merchant_id: str, request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    event_id = request.headers.get("X-Razorpay-Event-Id")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        event = container.ingestion.process_webhook(
            merchant_id=MerchantId(merchant_id),
            raw_body=raw_body,
            signature=signature,
            source_event_id=event_id,
            received_at=datetime.now(UTC),
        )
    except DuplicateWebhookEvent:
        return {"status": "duplicate"}
    except EventIngestionError as e:
        # Catch exception from verifier
        raise HTTPException(status_code=400, detail=f"Webhook validation failed: {e}")

    if event is None:
        return {"status": "duplicate"}

    # Process based on type
    try:
        from recoverai.domain.event import RevenueEventType

        if event.event_type == RevenueEventType.PAYMENT_FAILED:
            container.case_manager.create_or_update_from_event(event)
            container.global_conn.commit()
        elif event.event_type == RevenueEventType.PAYMENT_LINK_PAID:
            with container.tm.transaction() as conn:
                from recoverai.persistence.repositories.action import (
                    RecoveryActionRepository,
                )
                from recoverai.persistence.repositories.case import (
                    RecoveryCaseRepository,
                )

                action_repo = RecoveryActionRepository(conn)
                case_repo = RecoveryCaseRepository(conn)

                # Payment link events have the provider reference in external_reference
                if event.external_reference:
                    actions = action_repo.get_by_external_reference(
                        event.external_reference
                    )
                    for action in actions:
                        case = case_repo.get(action.case_id)
                        if case:
                            container.verification.reconcile_case(
                                case, datetime.now(UTC)
                            )
                            container.global_conn.commit()
    except Exception as e:  # noqa: BLE001  # noqa: BLE001  # noqa: BLE001
        import logging

        logging.getLogger(__name__).error(f"Error processing webhook event: {e}")
        # Return 200 so webhook is not retried if it's an internal error; it will be picked up by reconciliation

    return {"status": "processed"}


@app.get("/analytics", dependencies=[Depends(require_frontend_key)])
def get_analytics():
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.audit import AuditRepository
        from recoverai.persistence.repositories.verification import (
            VerificationRecordRepository,
        )

        repo = RecoveryCaseRepository(conn)
        action_repo = RecoveryActionRepository(conn)
        verif_repo = VerificationRecordRepository(conn)
        audit_repo = AuditRepository(conn)

        cur = conn.execute("SELECT case_id FROM recovery_cases")
        cases = []
        for row in cur.fetchall():
            c = repo.get(RecoveryCaseId(row["case_id"]))
            if c:
                cases.append(c)

        revenue_at_risk = {"INR": 0}
        verified_recovered = {"INR": 0}

        outcome_distribution = {
            "RECOVERED": 0,
            "EXECUTING": 0,
            "AWAITING_APPROVAL": 0,
            "ESCALATED": 0,
            "UNRECOVERABLE": 0,
            "VERIF_PENDING": 0,
        }

        funnel = {
            "DETECTED": len(cases),
            "ANALYZED": 0,
            "RECOMMENDED": 0,
            "HUMAN_APPROVAL": 0,
            "EXECUTING": 0,
            "RESPONDED": 0,
            "VERIFYING": 0,
            "VERIFIED": 0,
        }

        # Provenance
        recommendation_source = {"Gemini": 0, "Deterministic Fallback": 0}

        # Failure Causes
        failure_causes = {}

        # Verification Outcomes
        verification_outcomes = {
            "Provider Matched": 0,
            "Mismatch Detected": 0,
            "Verification Pending": 0,
        }

        # Intervention Strategies
        intervention_perf = {}

        total_eligible = 0
        total_verified_cases = 0

        total_verifications = 0
        total_verifications_matched = 0

        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        performance_7d = []
        for i in range(6, -1, -1):
            target_date = (now - timedelta(days=i)).date()
            performance_7d.append(
                {"date": target_date.isoformat(), "recovered": 0, "at_risk": 0}
            )

        for case in cases:
            curr = case.amount_at_risk.currency.value
            if curr not in revenue_at_risk:
                revenue_at_risk[curr] = 0
            if curr not in verified_recovered:
                verified_recovered[curr] = 0

            if case.status.value == "OPEN":
                revenue_at_risk[curr] += case.amount_at_risk.amount_minor

            # Recovery Outcomes logic
            st = case.workflow_state.value
            out_type = case.outcome_type.value if case.outcome_type else None

            if out_type == "RECOVERED":
                outcome_distribution["RECOVERED"] += 1
                verified_recovered[curr] += (
                    case.recovered_amount.amount_minor
                    if case.recovered_amount
                    else case.amount_at_risk.amount_minor
                )
                total_verified_cases += 1
            elif out_type in ("FAILED_PERMANENTLY", "DENIED"):
                outcome_distribution["UNRECOVERABLE"] += 1
            elif out_type == "ESCALATED" or st == "ESCALATED":
                outcome_distribution["ESCALATED"] += 1
            elif st == "WAITING_APPROVAL":
                outcome_distribution["AWAITING_APPROVAL"] += 1
            elif st in ("EXECUTING", "PENDING_EXECUTION"):
                outcome_distribution["EXECUTING"] += 1
            elif st in ("VERIFYING", "VERIFICATION_PENDING", "VERIFICATION_STARTED"):
                outcome_distribution["VERIF_PENDING"] += 1

            # Audit info extraction
            audit_events = audit_repo.get_by_case(case.case_id.value)
            provenance = None
            requires_human_approval = False
            for ae in audit_events:
                if ae.event_type.value == "LLM_RECOMMENDATION_CREATED" and ae.metadata:
                    actor_id = ae.actor.id if ae.actor else "UNKNOWN"
                    if (
                        "gemini" in actor_id.lower()
                        or "gemini" in str(ae.metadata).lower()
                    ):
                        provenance = "Gemini"
                    else:
                        provenance = "Deterministic Fallback"
                elif ae.event_type.value == "CASE_ESCALATED" or (
                    ae.event_type.value == "POLICY_DECISION_CREATED"
                    and ae.metadata
                    and ae.metadata.get("decision") == "ESCALATE"
                ):
                    requires_human_approval = True

            # Funnel Logic
            if st in (
                "ANALYZING",
                "POLICY_REVIEW",
                "WAITING_APPROVAL",
                "PENDING_EXECUTION",
                "EXECUTING",
                "VERIFYING",
                "CLOSED",
                "ESCALATED",
            ):
                funnel["ANALYZED"] += 1
                if provenance:
                    funnel["RECOMMENDED"] += 1

            if (
                st
                in (
                    "WAITING_APPROVAL",
                    "PENDING_EXECUTION",
                    "EXECUTING",
                    "VERIFYING",
                    "CLOSED",
                    "ESCALATED",
                )
                and requires_human_approval
            ):
                funnel["HUMAN_APPROVAL"] += 1

            if st in (
                "PENDING_EXECUTION",
                "EXECUTING",
                "VERIFYING",
                "CLOSED",
            ) and out_type not in ("DENIED", "ESCALATED"):
                funnel["EXECUTING"] += 1
                if st in ("VERIFYING", "CLOSED"):
                    funnel["RESPONDED"] += 1
                if st in ("VERIFYING", "CLOSED") and out_type != "FAILED_PERMANENTLY":
                    funnel["VERIFYING"] += 1

            if out_type == "RECOVERED":
                funnel["VERIFIED"] += 1

            # Provenance
            if provenance == "Gemini":
                recommendation_source["Gemini"] += 1
            elif provenance == "Deterministic Fallback":
                recommendation_source["Deterministic Fallback"] += 1

            # Actions for intervention
            actions = action_repo.get_by_case(case.case_id)
            for action in actions:
                s_type = (
                    action.action_type.value
                    if hasattr(action.action_type, "value")
                    else str(action.action_type)
                )
                if s_type not in intervention_perf:
                    intervention_perf[s_type] = {
                        "cases": 0,
                        "recovered": 0,
                        "failed": 0,
                        "pending": 0,
                    }
                intervention_perf[s_type]["cases"] += 1

                ast = (
                    action.status.value
                    if hasattr(action.status, "value")
                    else str(action.status)
                )
                if ast in ("VERIFIED_FAILURE", "EXECUTION_UNKNOWN", "CANCELLED"):
                    intervention_perf[s_type]["failed"] += 1
                    # Failure cause
                    cause = action.failure_reason or "Unknown Error"
                    failure_causes[cause] = failure_causes.get(cause, 0) + 1
                elif ast == "VERIFIED_SUCCESS" or (
                    ast == "COMPLETED" and out_type == "RECOVERED"
                ):
                    intervention_perf[s_type]["recovered"] += 1
                else:
                    intervention_perf[s_type]["pending"] += 1

            # Verification logic
            verifs = verif_repo.get_by_case(case.case_id)
            if verifs:
                total_verifications += 1
                v_st = (
                    verifs[0].verified_state.value
                    if hasattr(verifs[0].verified_state, "value")
                    else str(verifs[0].verified_state)
                )
                if v_st == "SUCCESS":
                    verification_outcomes["Provider Matched"] += 1
                    total_verifications_matched += 1
                elif v_st == "FAILURE":
                    verification_outcomes["Mismatch Detected"] += 1
                else:
                    verification_outcomes["Verification Pending"] += 1
            elif st in ("VERIFYING", "VERIFICATION_PENDING"):
                verification_outcomes["Verification Pending"] += 1

            if case.status.value != "OPEN" and out_type not in (
                "UNKNOWN_OR_MANUAL",
                "ESCALATED",
            ):
                total_eligible += 1

            # Performance Chart
            if case.status.value == "OPEN":
                case_date = case.opened_at.date()
                for day in performance_7d:
                    if day["date"] == case_date.isoformat():
                        day["at_risk"] += case.amount_at_risk.amount_minor

            if out_type == "RECOVERED":
                recovery_dt = case.closed_at or case.updated_at or case.opened_at
                recovery_date = recovery_dt.date()
                for day in performance_7d:
                    if day["date"] == recovery_date.isoformat():
                        day["recovered"] += (
                            case.recovered_amount.amount_minor
                            if case.recovered_amount
                            else case.amount_at_risk.amount_minor
                        )

        rec_rate = (
            (total_verified_cases / total_eligible * 100)
            if total_eligible > 0
            else None
        )
        verif_rate = (
            (total_verifications_matched / total_verifications * 100)
            if total_verifications > 0
            else None
        )

        int_perf_list = []
        for s_type, perf in intervention_perf.items():
            r_rate = (
                (perf["recovered"] / perf["cases"] * 100) if perf["cases"] > 0 else 0
            )
            int_perf_list.append(
                {
                    "strategy": s_type,
                    "cases": perf["cases"],
                    "recovered": perf["recovered"],
                    "failed": perf["failed"],
                    "pending": perf["pending"],
                    "recovery_rate": round(r_rate, 1),
                }
            )

        return {
            "recovery_rate": round(rec_rate, 1) if rec_rate is not None else None,
            "verification_rate": round(verif_rate, 1)
            if verif_rate is not None
            else None,
            "revenue_at_risk": revenue_at_risk,
            "verified_recovered": verified_recovered,
            "performance_7d": performance_7d,
            "recovery_outcomes": outcome_distribution,
            "intervention_performance": int_perf_list,
            "recommendation_source": recommendation_source,
            "lifecycle": [{"stage": k, "count": v} for k, v in funnel.items()],
            "failure_causes": [
                {"cause": k, "count": v} for k, v in failure_causes.items()
            ],
            "verification_outcomes": verification_outcomes,
        }


@app.post(
    "/recovery-cases/{case_id}/actions/{action_id}/approve",
    dependencies=[Depends(require_frontend_key)],
)
def approve_action(case_id: str, action_id: str):
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.case import RecoveryCaseRepository
        case = RecoveryCaseRepository(conn).get(RecoveryCaseId(case_id))
        if case and case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")
    try:
        result = container.mcp_registry.execute(
            "resume_recovery_action", {"case_id": case_id, "action_id": action_id}
        )
        return {"status": "success", "result": result}
    except Exception as e:  # noqa: BLE001
        if "INVALID_STATE" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/recovery-cases/{case_id}/abort", dependencies=[Depends(require_frontend_key)]
)
def abort_execution(case_id: str):
    with container.tm.transaction() as conn:
        from recoverai.domain.action import ActionStatus
        from recoverai.persistence.repositories.action import RecoveryActionRepository

        action_repo = RecoveryActionRepository(conn)
        actions = action_repo.get_by_case(RecoveryCaseId(case_id))
        if not actions:
            raise HTTPException(status_code=404, detail="No action found to abort")

        latest_action = max(actions, key=lambda x: x.requested_at)

        if latest_action.status in [ActionStatus.PROPOSED, ActionStatus.AUTHORIZED, ActionStatus.ESCALATED]:
            latest_action.status = ActionStatus.CANCELLED
            action_repo.update(latest_action)  # type: ignore
            
            from recoverai.persistence.repositories.audit import AuditRepository
            from recoverai.domain.audit import AuditEvent, AuditEventType, AuditActor, AuditActorType
            
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.ACTION_CANCELLED,
                    actor=AuditActor(type=AuditActorType.HUMAN, id="operator"),
                    case_id=latest_action.case_id,
                    action_id=latest_action.action_id,
                    metadata={"reason": "User aborted execution"}
                )
            )
            return {"status": "success", "message": "Execution aborted"}
        else:
            raise HTTPException(
                status_code=400, detail="Cannot abort action in current state"
            )


@app.get("/audit", dependencies=[Depends(require_frontend_key)])
async def get_audit_events():
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.audit import AuditRepository

        audit_repo = AuditRepository(conn)
        events = audit_repo.get_all(limit=1000)
        return {"events": [e.to_dict() for e in events]}
