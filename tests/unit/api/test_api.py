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
