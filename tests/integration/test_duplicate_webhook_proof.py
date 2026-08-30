import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app, container
from recoverai.config import settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    import os

    container.tm.run_migrations(
        os.path.join(
            os.path.dirname(__file__), "../../recoverai/persistence/migrations"
        )
    )
    with container.tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at) VALUES ('merch_1', 'Demo Merchant', 'USD', 'ACTIVE', '2023-01-01', '2023-01-01')"
        )


def sign_payload(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def test_duplicate_webhook():
    secret = settings.razorpay_webhook_secret or "secret"
    payload = json.dumps(
        {
            "event": "payment.failed",
            "payload": {
                "payment": {
                    "entity": {"id": "pay_dup_001", "amount": 1500, "currency": "USD"}
                }
            },
            "created_at": int(datetime.now(UTC).timestamp()),
        }
    )
    signature = sign_payload(payload, secret)
    headers = {"X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": "evt_dup_999"}

    # First request
    resp1 = client.post("/webhooks/razorpay/merch_1", content=payload, headers=headers)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "processed"

    # Second request
    resp2 = client.post("/webhooks/razorpay/merch_1", content=payload, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "duplicate"
