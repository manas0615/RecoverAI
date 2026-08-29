import os
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
    # mock config for testing
    from recoverai.config import settings

    settings.razorpay_mode = "test"

    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_1', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )


@mock.patch("urllib.request.urlopen")
def test_golden_path(mock_urlopen):
    # 1. Simulate PAYMENT_FAILED event ingested via WebhookIngestionService (normally called by the webhook endpoint)
    # But wait, we can just call the endpoint directly, but we need Razorpay signature.
    # We can bypass signature for testing or mock the webhook parsing.

    # Mocking webhook process logic:
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

    # Call create_or_update_from_event directly as it's triggered from webhook or reconciliation
    case = container.case_manager.create_or_update_from_event(event)
    assert case is not None

    # 2. Simulate MCP calling create_payment_link
    action_id = f"act_{uuid.uuid4().hex[:8]}"

    # Mock Razorpay Provider Response
    def urlopen_side_effect(req, *args, **kwargs):
        cm = mock.MagicMock()
        resp = mock.MagicMock()
        if "razorpay.com" in req.full_url:
            resp.read.return_value = (
                b'{"id": "plink_test_gold", "short_url": "http://test.link"}'
            )
        else:
            resp.read.return_value = b"{}"
        cm.__enter__.return_value = resp
        return cm

    mock_urlopen.side_effect = urlopen_side_effect

    mcp_payload = {
        "tool": "create_payment_link",
        "args": {"case_id": case.case_id.value, "action_id": action_id},
    }

    # Needs require_n8n_key dependency, override or pass correct header
    from recoverai.config import settings

    headers = {"X-API-Key": settings.n8n_api_key or "mock"}

    res = client.post("/mcp/execute", json=mcp_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    if "data" in data:
        data = data["data"]
    assert data["provider_reference"] == "plink_test_gold"

    # Check n8n was triggered (mock_n8n_urlopen)
    # assert mock_urlopen.called

    # 3. Simulate PAYMENT_LINK_PAID
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.event import RevenueEventRepository

        event_paid = RevenueEvent(
            event_id=RevenueEventId(f"evt_{uuid.uuid4().hex[:8]}"),
            event_type=RevenueEventType.PAYMENT_LINK_PAID,
            source=EventSource(
                EventSourceType.RAZORPAY_WEBHOOK, f"webev_{uuid.uuid4().hex[:8]}"
            ),
            merchant_id=MerchantId("merch_1"),
            amount=Money(1000, CurrencyCode.USD),
            external_reference="plink_test_gold",
            occurred_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
        )
        RevenueEventRepository(conn).save(event_paid)

    # Invoke reconciliation
    container.global_conn.commit()
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.case import RecoveryCaseRepository

        case = RecoveryCaseRepository(conn).get(case.case_id)
        container.verification.reconcile_case(case, datetime.now(UTC))
        container.global_conn.commit()

    with container.tm.transaction() as conn:
        case = RecoveryCaseRepository(conn).get(case.case_id)
        assert case.status.name == "CLOSED"
        assert case.outcome_type.name == "RECOVERED"
