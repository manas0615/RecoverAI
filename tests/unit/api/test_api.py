import os

os.environ["ENVIRONMENT"] = "test"
os.environ["FRONTEND_API_KEY"] = "test_frontend_key"
os.environ["N8N_API_KEY"] = "test_n8n_key"
os.environ["FRONTEND_CORS_ORIGIN"] = "http://localhost:5173"

from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)

FRONTEND_HEADERS = {"X-API-Key": settings.frontend_api_key}
N8N_HEADERS = {"X-API-Key": settings.n8n_api_key}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mcp_execute_no_key():
    response = client.post("/mcp/execute", json={"tool": "unknown_tool", "args": {}})
    assert response.status_code == 401


def test_mcp_execute_invalid_key():
    response = client.post(
        "/mcp/execute",
        headers={"X-API-Key": "invalid"},
        json={"tool": "unknown_tool", "args": {}},
    )
    assert response.status_code == 401


def test_mcp_execute_frontend_key():
    response = client.post(
        "/mcp/execute",
        headers=FRONTEND_HEADERS,
        json={"tool": "unknown_tool", "args": {}},
    )
    assert response.status_code == 403
    assert "Insufficient role" in response.json()["detail"]


def test_mcp_execute_unknown_tool():
    response = client.post(
        "/mcp/execute",
        headers=N8N_HEADERS,
        json={"tool": "unknown_tool", "args": {}},
    )
    assert response.status_code == 400
    assert "Unknown tool" in response.json()["detail"]


def test_mcp_execute_valid_tool():
    # Calling a read tool
    response = client.post(
        "/mcp/execute",
        headers=N8N_HEADERS,
        json={"tool": "get_recovery_case", "args": {"case_id": "nonexistent"}},
    )
    # Since it's MCP execution, the MCP tool returns a structured format
    assert response.status_code == 200
    assert response.json()["error"] == "Case nonexistent not found"


def test_get_cases_no_key():
    response = client.get("/recovery-cases")
    assert response.status_code == 401


def test_get_cases_invalid_key():
    response = client.get("/recovery-cases", headers={"X-API-Key": "invalid"})
    assert response.status_code == 401


def test_get_cases():
    response = client.get("/recovery-cases", headers=FRONTEND_HEADERS)
    assert response.status_code == 200
    assert "cases" in response.json()


def test_get_case_not_found():
    response = client.get("/recovery-cases/missing", headers=FRONTEND_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Case not found"


def test_get_timeline():
    response = client.get("/recovery-cases/missing/timeline", headers=FRONTEND_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"events": []}


def test_webhook_missing_signature():
    response = client.post(
        "/webhooks/razorpay/M_test",
        data=b"raw",
        headers={"X-Razorpay-Event-Id": "evt_1"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing signature"


def test_webhook_invalid_signature():
    response = client.post(
        "/webhooks/razorpay/M_test",
        data=b"raw",
        headers={"X-Razorpay-Signature": "invalid", "X-Razorpay-Event-Id": "evt_1"},
    )
    assert response.status_code == 400
    assert "Webhook validation failed" in response.json()["detail"]


def test_webhook_api_key_does_not_bypass():
    # Sending valid API key but missing signature should still fail HMAC check
    response = client.post(
        "/webhooks/razorpay/M_test",
        data=b"raw",
        headers={"X-API-Key": settings.n8n_api_key, "X-Razorpay-Event-Id": "evt_1"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing signature"


def test_analytics_no_key():
    response = client.get("/analytics")
    assert response.status_code == 401


def test_analytics():
    response = client.get("/analytics", headers=FRONTEND_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "recovery_rate" in data
    assert "verification_rate" in data
    assert "revenue_at_risk" in data
    assert "verified_recovered" in data
    assert "performance_7d" in data
    assert "recovery_outcomes" in data
    assert "intervention_performance" in data
    assert "recommendation_source" in data
    assert "lifecycle" in data
    assert "failure_causes" in data
    assert "verification_outcomes" in data


def test_analyze_case_not_found():
    response = client.post("/recovery-cases/missing/analyze", headers=FRONTEND_HEADERS)
    assert response.status_code == 404
    assert response.json()["detail"] == "Case not found"


def clear_db():
    from recoverai.api.main import container

    with container.tm.transaction() as conn:
        conn.execute("DELETE FROM verification_records")
        conn.execute("DELETE FROM recovery_actions")
        conn.execute("DELETE FROM policy_decisions")
        conn.execute("DELETE FROM audit_events")
        conn.execute("DELETE FROM case_source_events")
        conn.execute("DELETE FROM recovery_cases")
        conn.execute("DELETE FROM revenue_events")
        conn.execute("DELETE FROM customers")
        conn.execute("DELETE FROM merchants")


def test_populated_data_contracts():
    clear_db()

    from datetime import UTC, datetime

    from recoverai.api.main import container
    from recoverai.domain.action import (
        ActionStatus,
        ActionType,
        PolicyDecisionId,
        RecoveryAction,
        RecoveryActionId,
    )
    from recoverai.domain.audit import (
        AuditActor,
        AuditActorType,
        AuditEvent,
        AuditEventType,
    )
    from recoverai.domain.case import RecoveryCase, RevenueSource
    from recoverai.domain.identifiers import MerchantId, RecoveryCaseId, RevenueEventId
    from recoverai.domain.money import CurrencyCode, Money, RevenueAmount

    now = datetime.now(UTC)

    case = RecoveryCase(
        case_id=RecoveryCaseId("case_populated"),
        merchant_id=MerchantId("merch_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(10000, CurrencyCode.INR)),
        opened_at=now,
        source_event_ids={RevenueEventId("evt_1")},
    )

    action = RecoveryAction(
        action_id=RecoveryActionId("act_1"),
        case_id=case.case_id,
        action_type=ActionType.CREATE_PAYMENT_LINK,
        requested_at=now,
        policy_decision_id=PolicyDecisionId("dec_1"),
        status=ActionStatus.PROPOSED,
    )

    audit_event = AuditEvent(
        event_type=AuditEventType.LLM_RECOMMENDATION_CREATED,
        actor=AuditActor(type=AuditActorType.LLM_AGENT, id="gemini-1.5"),
        case_id=case.case_id,
        timestamp=now,
        metadata={"recommended_action": "CREATE_PAYMENT_LINK", "confidence": 0.95},
    )

    from recoverai.domain.event import (
        EventSource,
        EventSourceType,
        RevenueEvent,
        RevenueEventType,
    )

    event = RevenueEvent(
        event_id=RevenueEventId("evt_1"),
        event_type=RevenueEventType.PAYMENT_FAILED,
        merchant_id=MerchantId("merch_1"),
        occurred_at=now,
        received_at=now,
        source=EventSource(
            source_type=EventSourceType.RAZORPAY_WEBHOOK, source_event_id="wh"
        ),
        amount=Money(10000, CurrencyCode.INR),
    )

    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT INTO merchants (merchant_id, display_name, status, default_currency, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "merch_1",
                "Test Merchant",
                "ACTIVE",
                "INR",
                now.isoformat(),
                now.isoformat(),
            ),
        )

        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.persistence.repositories.audit import AuditRepository
        from recoverai.persistence.repositories.case import RecoveryCaseRepository
        from recoverai.persistence.repositories.event import RevenueEventRepository

        RevenueEventRepository(conn).save(event)
        RecoveryCaseRepository(conn).save(case)

        conn.execute(
            "INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "dec_1",
                "case_populated",
                "act_1",
                "APPROVE",
                "1.0",
                "[]",
                "[]",
                now.isoformat(),
            ),
        )

        RecoveryActionRepository(conn).save(action)
        AuditRepository(conn).append(audit_event)

    # Test case detail populated
    response = client.get(
        f"/recovery-cases/{case.case_id.value}", headers=FRONTEND_HEADERS
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recommendation"] == "CREATE_PAYMENT_LINK"
    assert data["provenance"] == "Gemini"
    assert data["action_id"] == "act_1"

    # Test analytics populated
    response = client.get("/analytics", headers=FRONTEND_HEADERS)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recommendation_source"]["Gemini"] == 1

    clear_db()
