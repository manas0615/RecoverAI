import hashlib
import hmac

import pytest

from recoverai.ingestion.exceptions import InvalidWebhookSignature
from recoverai.ingestion.razorpay.signature import WebhookVerifier


def test_signature_validation_success():
    secret = "my_secret"
    payload = b'{"event":"payment.failed"}'

    expected_sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    verifier = WebhookVerifier(secret)
    verifier.verify(payload, expected_sig)


def test_signature_validation_fails_on_tampering():
    secret = "my_secret"
    payload = b'{"event":"payment.failed"}'
    tampered_payload = b'{"event":"payment.captured"}'

    expected_sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    verifier = WebhookVerifier(secret)
    with pytest.raises(InvalidWebhookSignature):
        verifier.verify(tampered_payload, expected_sig)


def test_signature_validation_fails_on_missing_signature():
    secret = "my_secret"
    payload = b'{"event":"payment.failed"}'

    verifier = WebhookVerifier(secret)
    with pytest.raises(InvalidWebhookSignature):
        verifier.verify(payload, None)

    with pytest.raises(InvalidWebhookSignature):
        verifier.verify(payload, "")


def test_signature_fails_on_equivalent_json_different_bytes():
    secret = "my_secret"
    # Same logical JSON, different formatting
    payload1 = b'{"event":"payment.failed"}'
    payload2 = b'{\n  "event": "payment.failed"\n}'

    sig1 = hmac.new(secret.encode(), payload1, hashlib.sha256).hexdigest()

    verifier = WebhookVerifier(secret)
    # sig1 validates against payload1
    verifier.verify(payload1, sig1)

    # but fails against payload2
    with pytest.raises(InvalidWebhookSignature):
        verifier.verify(payload2, sig1)
