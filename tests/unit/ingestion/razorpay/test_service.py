import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest

from recoverai.domain import MerchantId
from recoverai.ingestion.exceptions import (
    DuplicateWebhookEvent,
    MalformedWebhookPayload,
)
from recoverai.ingestion.razorpay.normalizer import RazorpayNormalizer
from recoverai.ingestion.razorpay.service import WebhookIngestionService
from recoverai.ingestion.razorpay.signature import WebhookVerifier


def test_service_ingestion_and_deduplication(tm):
    now = datetime.now(UTC)
    secret = "my_secret"
    verifier = WebhookVerifier(secret)
    normalizer = RazorpayNormalizer()
    service = WebhookIngestionService(verifier, normalizer, tm)

    payload_dict = {
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_123",
                    "amount": 5000,
                    "currency": "INR",
                    "created_at": 1600000000,
                }
            }
        },
    }
    raw_body = json.dumps(payload_dict).encode("utf-8")
    sig = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

    # 1. First time should ingest successfully
    ev1 = service.process_webhook(MerchantId("m_1"), raw_body, sig, "razor_evt_1", now)
    assert ev1 is not None
    assert ev1.source.source_event_id == "razor_evt_1"

    # 2. Second time with exact same event ID should raise DuplicateWebhookEvent
    with pytest.raises(DuplicateWebhookEvent):
        service.process_webhook(MerchantId("m_1"), raw_body, sig, "razor_evt_1", now)

    # 3. Same payload but different event ID (e.g. razorpay retrying with new ID?) should succeed
    ev3 = service.process_webhook(MerchantId("m_1"), raw_body, sig, "razor_evt_2", now)
    assert ev3 is not None


def test_service_malformed_json_fails_safely(tm):
    now = datetime.now(UTC)
    secret = "my_secret"
    verifier = WebhookVerifier(secret)
    normalizer = RazorpayNormalizer()
    service = WebhookIngestionService(verifier, normalizer, tm)

    raw_body = b'{"event": "payment.fai'
    sig = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

    with pytest.raises(MalformedWebhookPayload, match="Invalid JSON body"):
        service.process_webhook(MerchantId("m_1"), raw_body, sig, "evt_3", now)
