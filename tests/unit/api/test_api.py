import os

os.environ["ENVIRONMENT"] = "test"

from fastapi.testclient import TestClient

from recoverai.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mcp_execute_unknown_tool():
    response = client.post("/mcp/execute", json={"tool": "unknown_tool", "args": {}})
    assert response.status_code == 400
    assert "Unknown tool" in response.json()["detail"]


def test_mcp_execute_valid_tool():
    # Calling a read tool
    response = client.post(
        "/mcp/execute",
        json={"tool": "get_recovery_case", "args": {"case_id": "nonexistent"}},
    )
    # Since it's MCP execution, the MCP tool returns a structured format
    assert response.status_code == 200
    assert response.json()["error"] == "Case nonexistent not found"


def test_get_cases():
    response = client.get("/recovery-cases")
    assert response.status_code == 200
    assert "cases" in response.json()


def test_get_case_not_found():
    response = client.get("/recovery-cases/missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "Case not found"


def test_get_timeline():
    response = client.get("/recovery-cases/missing/timeline")
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
