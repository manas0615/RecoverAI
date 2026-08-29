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

        if os.environ.get("ENVIRONMENT") == "test" or settings.environment == "test":
            db_name = f"file:mem_{uuid.uuid4().hex}?mode=memory&cache=shared"
            self.tm = TransactionManager(f"sqlite:///{db_name}")
        else:
            self.tm = TransactionManager(settings.database_url)

        # Keep global connection open first so the DB is not destroyed
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

        self.mcp_context = MCPContext(
            tm=self.tm,
            policy_engine=self.policy,
            razorpay_service=self.rzp_service,
            state_machine=RecoveryStateMachine(self.tm),
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
        "case_id": str(case.case_id),
        "merchant_id": str(case.merchant_id),
        "customer_id": str(case.customer_id),
        "status": case.status.value,
        "created_at": case.created_at.isoformat(),
        "amount_minor": case.opportunity_amount.amount_minor,
        "currency": case.opportunity_amount.currency.value,
        "verification_count": case.verification_count,
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
        repo = RecoveryCaseRepository(conn)
        try:
            case = repo.get(RecoveryCaseId(case_id))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid case ID")
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return case_to_dict(case)


@app.get(
    "/recovery-cases/{case_id}/timeline", dependencies=[Depends(require_frontend_key)]
)
def get_case_timeline(case_id: str):
    with container.tm.transaction() as conn:
        repo = AuditRepository(conn)
        events = repo.get_by_case(case_id)
        return {"events": [e.to_dict() for e in events]}


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
    return {"status": "processed"}
