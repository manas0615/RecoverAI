import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings
from recoverai.persistence.connection import TransactionManager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def seed_test_db():
    tm = TransactionManager(settings.database_url)
    with tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_demo', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO customers (customer_id, merchant_id, display_name, created_at, updated_at) VALUES ('cust_demo', 'merch_demo', 'Demo Customer', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )


def test_real_razorpay_e2e_recovery(client):
    import os

    if os.environ.get("ALLOW_REAL_RAZORPAY") != "1":
        pytest.skip(
            "Skipping real Razorpay E2E test due to missing ALLOW_REAL_RAZORPAY=1 explicit opt-in"
        )

    if not (
        settings.razorpay_key_id
        and settings.razorpay_key_secret
        and settings.razorpay_webhook_secret
    ):
        pytest.skip("Skipping real Razorpay E2E test due to missing credentials")

    if settings.razorpay_mode != "test":
        pytest.fail("Cannot run E2E test in non-test mode")

    merchant_id = "merch_demo"
    customer_id = "cust_demo"
    amount = 50000
    currency = "INR"

    # 1. Trigger payment.failed webhook
    event_payload = {
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_{uuid.uuid4().hex[:12]}",
                    "amount": amount,
                    "currency": currency,
                    "customer_id": customer_id,
                    "status": "failed",
                    "error_code": "BAD_REQUEST_ERROR",
                }
            }
        },
        "created_at": int(datetime.now(UTC).timestamp()),
    }

    body = json.dumps(event_payload, separators=(",", ":"))
    signature = hmac.new(
        settings.razorpay_webhook_secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    resp = client.post(
        f"/webhooks/razorpay/{merchant_id}",
        content=body,
        headers={
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": event_id,
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200, f"Webhook failed: {resp.text}"

    # Test deduplication: send identical webhook again
    resp_dup = client.post(
        f"/webhooks/razorpay/{merchant_id}",
        content=body,
        headers={
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": event_id,
            "Content-Type": "application/json",
        },
    )
    assert resp_dup.status_code == 200
    assert resp_dup.json() == {"status": "duplicate"}

    # Test Invalid HMAC signature
    resp_invalid = client.post(
        f"/webhooks/razorpay/{merchant_id}",
        content=body,
        headers={
            "X-Razorpay-Signature": "invalid_signature",
            "X-Razorpay-Event-Id": f"ev_{uuid.uuid4().hex[:12]}",
            "Content-Type": "application/json",
        },
    )
    assert resp_invalid.status_code == 400

    # 2. Get cases
    resp = client.get(
        "/recovery-cases/", headers={"X-API-Key": settings.frontend_api_key}
    )
    assert resp.status_code == 200
    cases = resp.json()["cases"]

    # Find our new case
    case = next(
        (
            c
            for c in cases
            if c["customer_id"] == customer_id and c["amount_minor"] == amount
        ),
        None,
    )
    assert case is not None, "Case was not created"
    case_id = case["case_id"]

    # 3. Analyze Case (simulate Gemini or Deterministic fallback)
    resp = client.post(
        f"/recovery-cases/{case_id}/analyze",
        headers={"X-API-Key": settings.frontend_api_key},
    )
    assert resp.status_code == 200, resp.text
    analyze_result = resp.json()
    assert analyze_result["status"] == "success"

    # 4. Trigger Execution via MCP
    act_id = f"act_{uuid.uuid4().hex[:8]}"
    resp = client.post(
        "/mcp/execute",
        headers={"X-API-Key": settings.n8n_api_key},
        json={
            "tool": "create_payment_link",
            "args": {"case_id": case_id, "action_id": act_id},
        },
    )
    assert resp.status_code == 200, resp.text

    # Re-fetch cases to check status
    resp = client.get(
        "/recovery-cases/", headers={"X-API-Key": settings.frontend_api_key}
    )
    assert resp.status_code == 200
    cases = resp.json()["cases"]
    case_summary = next(c for c in cases if c["case_id"] == case_id)

    action_status = case_summary["action_status"]
    assert action_status == "VERIFICATION_PENDING"
    assert case_summary["external_reference"] is not None
    assert case_summary["external_reference"].startswith("plink_")

    plink_id = case_summary["external_reference"]

    # 5. Deliver payment_link.paid webhook with CORRECT amount
    paid_payload = {
        "event": "payment_link.paid",
        "contains": ["payment_link"],
        "payload": {
            "payment_link": {
                "entity": {
                    "id": plink_id,
                    "amount": amount,
                    "currency": currency,
                    "customer_id": customer_id,
                    "status": "paid",
                }
            }
        },
        "created_at": int(datetime.now(UTC).timestamp()),
    }
    body2 = json.dumps(paid_payload, separators=(",", ":"))
    signature2 = hmac.new(
        settings.razorpay_webhook_secret.encode("utf-8"),
        body2.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    event_id2 = f"ev_{uuid.uuid4().hex[:12]}"

    resp = client.post(
        f"/webhooks/razorpay/{merchant_id}",
        content=body2,
        headers={
            "X-Razorpay-Signature": signature2,
            "X-Razorpay-Event-Id": event_id2,
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200

    # 6. Verify success
    resp = client.get(
        "/recovery-cases/", headers={"X-API-Key": settings.frontend_api_key}
    )
    cases = resp.json()["cases"]
    case_summary = next(c for c in cases if c["case_id"] == case_id)

    assert case_summary["action_status"] == "VERIFIED_SUCCESS"
    assert case_summary["status"] == "CLOSED"
