import os
import urllib.error
import uuid
from datetime import UTC, datetime
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app, container
from recoverai.domain.event import (
    EventSource,
    EventSourceType,
    RevenueEvent,
    RevenueEventType,
)
from recoverai.domain.identifiers import MerchantId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    container.tm.run_migrations(
        os.path.join(
            os.path.dirname(__file__), "../../recoverai/persistence/migrations"
        )
    )
    from recoverai.config import settings

    settings.razorpay_mode = "test"

    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_1', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )


def _setup_case():
    payment_id = f"pay_{uuid.uuid4().hex[:8]}"
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        event = RevenueEvent(
            event_id=RevenueEventId(f"evt_{uuid.uuid4().hex[:8]}"),
            event_type=RevenueEventType.PAYMENT_FAILED,
            source=EventSource(EventSourceType.RAZORPAY_WEBHOOK, payment_id),
            merchant_id=MerchantId("merch_1"),
            amount=Money(1000, CurrencyCode.USD),
            occurred_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
        )
        RevenueEventRepository(conn).save(event)
    return container.case_manager.create_or_update_from_event(event)


@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_network_unknown(mock_rzp_urlopen):
    case = _setup_case()
    action_id = f"act_{uuid.uuid4().hex[:8]}"

    mock_rzp_urlopen.side_effect = TimeoutError("Timeout")

    mcp_payload = {
        "tool": "create_payment_link",
        "args": {"case_id": case.case_id.value, "action_id": action_id},
    }
    from recoverai.config import settings

    headers = {"X-API-Key": settings.n8n_api_key or "mock"}

    res = client.post("/mcp/execute", json=mcp_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["code"] == "EXTERNAL_EXECUTION_UNCERTAINTY"

    # State should be EXECUTION_UNKNOWN
    with container.tm.transaction() as conn:
        from recoverai.domain.identifiers import RecoveryActionId
        from recoverai.persistence.repositories.action import RecoveryActionRepository

        action = RecoveryActionRepository(conn).get(RecoveryActionId(action_id))
        assert action.status.name == "EXECUTION_UNKNOWN"


@mock.patch("recoverai.integrations.razorpay.adapter.urllib.request.urlopen")
def test_provider_rejected(mock_rzp_urlopen):
    case = _setup_case()
    action_id = f"act_{uuid.uuid4().hex[:8]}"

    mock_rzp_urlopen.side_effect = urllib.error.HTTPError(
        "url", 400, "Bad Request", {}, None
    )

    mcp_payload = {
        "tool": "create_payment_link",
        "args": {"case_id": case.case_id.value, "action_id": action_id},
    }
    from recoverai.config import settings

    headers = {"X-API-Key": settings.n8n_api_key or "mock"}

    res = client.post("/mcp/execute", json=mcp_payload, headers=headers)

    # Should not raise MCPError! Provider rejected completes execution synchronously and moves to VERIFICATION_PENDING (failed verification handled by P09 later)
    # Wait, earlier in the code it returns the execution result.
    assert res.status_code == 200

    with container.tm.transaction() as conn:
        from recoverai.domain.identifiers import RecoveryActionId
        from recoverai.persistence.repositories.action import RecoveryActionRepository

        action = RecoveryActionRepository(conn).get(RecoveryActionId(action_id))
        assert action.status.name == "VERIFICATION_PENDING"
