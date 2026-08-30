import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    import os

    from recoverai.api.main import container

    container.tm.run_migrations(
        os.path.join(
            os.path.dirname(__file__), "../../recoverai/persistence/migrations"
        )
    )
    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('test_merchant', 'Test Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )


def sign_payload(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def test_invalid_hmac_rejected():
    payload = json.dumps({"event": "payment.failed"})
    # No signature
    resp = client.post("/webhooks/razorpay/test_merchant", content=payload)
    assert resp.status_code == 400
    assert "Missing signature" in resp.json()["detail"]

    # Invalid signature
    resp = client.post(
        "/webhooks/razorpay/test_merchant",
        content=payload,
        headers={"X-Razorpay-Signature": "invalid", "X-Razorpay-Event-Id": "evt_123"},
    )
    assert resp.status_code == 400
    assert "Signature mismatch" in resp.json()["detail"]


def test_tampered_payload_rejected():
    secret = settings.razorpay_webhook_secret or "secret"
    payload = json.dumps({"event": "payment.failed", "amount": 1000})
    signature = sign_payload(payload, secret)

    # Tampered body
    tampered_payload = json.dumps({"event": "payment.failed", "amount": 90000})
    resp = client.post(
        "/webhooks/razorpay/test_merchant",
        content=tampered_payload,
        headers={"X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": "evt_123"},
    )
    assert resp.status_code == 400
    assert "Signature mismatch" in resp.json()["detail"]
