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
from recoverai.ingestion.exceptions import EventIngestionError
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
                except Exception as e:  # noqa: BLE001  # noqa: BLE001
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
        cases = []
        for row in cur.fetchall():
            c = repo.get(RecoveryCaseId(row["case_id"]))
            if c:
                cases.append(case_to_dict(c))
        return {"cases": cases}


@app.get("/recovery-cases/{case_id}", dependencies=[Depends(require_frontend_key)])
def get_case(case_id: str):
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        repo = RecoveryCaseRepository(conn)
        event_repo = RevenueEventRepository(conn)
        try:
            case = repo.get(RecoveryCaseId(case_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid case ID")
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        events = [event_repo.get(eid) for eid in case.source_event_ids]

        result = case_to_dict(case)
        result["events"] = [
            {
                "event_id": e.event_id.value,
                "event_type": e.event_type.value,
                "amount_minor": e.amount.amount_minor if e.amount else None,
                "currency": e.amount.currency.value if e.amount else None,
                "occurred_at": e.occurred_at.isoformat(),
                "external_reference": e.external_reference,
            }
            for e in events
            if e
        ]
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

        events = [event_repo.get(eid) for eid in case.source_event_ids]

    try:
        from datetime import UTC, datetime

        from recoverai.domain.audit import (
            AuditActor,
            AuditActorType,
            AuditEvent,
            AuditEventType,
        )
        from recoverai.persistence.repositories.audit import AuditRepository
        from recoverai.policy.engine import PolicyContext

        with container.tm.transaction() as conn:
            audit_repo = AuditRepository(conn)

            # 1. Run Intelligence
            risk, cause, plan = container.intelligence.analyze(case, events)

            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.LLM_RECOMMENDATION_CREATED,
                    actor=AuditActor(type=AuditActorType.LLM_AGENT, id=risk.model_name),
                    case_id=case.case_id,
                    timestamp=datetime.now(UTC),
                    metadata={
                        "recommended_action": plan.selected_action_type.value
                        if plan.selected_action_type
                        else "UNKNOWN",
                        "reasoning": plan.selection_reason,
                        "confidence": cause.confidence.value if cause else None,
                        "cause_category": cause.category if cause else None,
                        "recovery_probability": risk.recovery_probability.value,
                        "expected_recovery_amount": plan.expected_recovery_value.amount_minor
                        if plan.expected_recovery_value
                        else (
                            risk.expected_recovery_value.amount_minor
                            if risk.expected_recovery_value
                            else 0
                        ),
                        "expected_recovery_currency": plan.expected_recovery_value.currency.value
                        if plan.expected_recovery_value
                        else (
                            risk.expected_recovery_value.currency.value
                            if risk.expected_recovery_value
                            else "USD"
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
                        ),
                        "model_version": risk.model_version,
                    },
                )
            )

            # 2. Evaluate Policy
            policy_context = PolicyContext(
                policy_version="1.0", current_time=datetime.now(UTC)
            )
            decision = container.policy.evaluate(policy_context, case, plan, [])

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

            # 3. Do NOT auto-execute (as requested by instructions)
            return {
                "status": "success",
                "recommendation": plan.selected_action_type.value
                if plan.selected_action_type
                else "UNKNOWN",
                "recommendation_reason": plan.selection_reason,
                "expected_recovery_value": plan.expected_recovery_value.amount_minor
                if plan.expected_recovery_value
                else (
                    risk.expected_recovery_value.amount_minor
                    if risk.expected_recovery_value
                    else 0
                ),
                "recovery_probability": risk.recovery_probability.value,
                "probability_meaning": getattr(
                    risk.recovery_probability,
                    "reasoning",
                    "Derived from historical failure count and systemic signals",
                ),
                "cause_category": cause.category if cause else "UNKNOWN",
                "cause_confidence": cause.confidence.value if cause else 0.0,
                "policy_decision": decision.decision.value,
                "policy_reasons": decision.reason_codes,
                "model_version": risk.model_version,
            }
    except Exception as e:  # noqa: BLE001
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
    except Exception as e:  # noqa: BLE001  # noqa: BLE001
        import logging

        logging.getLogger(__name__).error(f"Error processing webhook event: {e}")
        # Return 200 so webhook is not retried if it's an internal error; it will be picked up by reconciliation

    return {"status": "processed"}


@app.get("/analytics", dependencies=[Depends(require_frontend_key)])
def get_analytics():
    with container.tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        cur = conn.execute("SELECT case_id FROM recovery_cases")
        cases = []
        for row in cur.fetchall():
            c = repo.get(RecoveryCaseId(row["case_id"]))
            if c:
                cases.append(c)

        revenue_at_risk = {}
        verified_recovered = {}
        unknown_exposure = {}
        active_cases = 0
        outcome_distribution = {
            "RECOVERED": 0,
            "FAILED": 0,
            "UNKNOWN": 0,
            "DENIED": 0,
            "ESCALATED": 0,
        }
        funnel = {
            "DETECTED": len(cases),
            "ANALYZED": 0,
            "APPROVED": 0,
            "EXECUTING": 0,
            "VERIFIED": 0,
        }

        for case in cases:
            curr = case.amount_at_risk.currency.value
            for d in (revenue_at_risk, verified_recovered, unknown_exposure):
                if curr not in d:
                    d[curr] = 0

            if case.status.value == "OPEN":
                revenue_at_risk[curr] += case.amount_at_risk.amount_minor
                active_cases += 1
                unknown_exposure[curr] += case.amount_at_risk.amount_minor

            if case.outcome_type:
                out = case.outcome_type.value
                if out == "RECOVERED":
                    outcome_distribution["RECOVERED"] += 1
                    verified_recovered[curr] += (
                        case.recovered_amount.amount_minor
                        if case.recovered_amount
                        else case.amount_at_risk.amount_minor
                    )
                elif out == "FAILED_PERMANENTLY":
                    outcome_distribution["FAILED"] += 1
                elif out == "UNKNOWN_OR_MANUAL":
                    outcome_distribution["UNKNOWN"] += 1
                    unknown_exposure[curr] += case.amount_at_risk.amount_minor
                elif out == "DENIED":
                    outcome_distribution["DENIED"] += 1
                elif out == "ESCALATED":
                    outcome_distribution["ESCALATED"] += 1
                else:
                    outcome_distribution["UNKNOWN"] += 1

            state = case.workflow_state.value
            if state in (
                "ANALYZING",
                "POLICY_REVIEW",
                "PENDING_EXECUTION",
                "EXECUTING",
                "VERIFYING",
                "CLOSED",
            ):
                funnel["ANALYZED"] += 1
            if state in ("PENDING_EXECUTION", "EXECUTING", "VERIFYING", "CLOSED"):
                if not (
                    case.outcome_type
                    and case.outcome_type.value in ("DENIED", "ESCALATED")
                ):
                    funnel["APPROVED"] += 1
            if state in ("EXECUTING", "VERIFYING", "CLOSED"):
                if not (
                    case.outcome_type
                    and case.outcome_type.value in ("DENIED", "ESCALATED")
                ):
                    funnel["EXECUTING"] += 1
            if (
                state == "CLOSED"
                and case.outcome_type
                and case.outcome_type.value == "RECOVERED"
            ):
                funnel["VERIFIED"] += 1

        return {
            "revenue_at_risk": revenue_at_risk,
            "verified_recovered": verified_recovered,
            "active_cases": active_cases,
            "unknown_exposure": unknown_exposure,
            "outcomeDistribution": [
                {"name": k, "value": v} for k, v in outcome_distribution.items()
            ],
            "funnel": [{"stage": k.title(), "count": v} for k, v in funnel.items()],
        }
