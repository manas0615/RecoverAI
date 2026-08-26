import hashlib
import hmac

from recoverai.ingestion.exceptions import InvalidWebhookSignature


class WebhookVerifier:
    """
    Validates Razorpay webhook signatures according to standard HMAC-SHA256 rules.
    """

    def __init__(self, webhook_secret: str):
        if not webhook_secret:
            raise ValueError("Webhook secret cannot be empty")
        self._secret = webhook_secret.encode("utf-8")

    def verify(self, raw_body: bytes, received_signature: str | None) -> None:
        """
        Verifies the signature in constant time.
        Raises InvalidWebhookSignature if validation fails.
        """
        if not received_signature:
            raise InvalidWebhookSignature("Missing X-Razorpay-Signature")

        expected_signature = hmac.new(
            self._secret, raw_body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, received_signature):
            raise InvalidWebhookSignature("Signature mismatch")
