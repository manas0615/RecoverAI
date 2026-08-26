import json
import logging
from datetime import datetime

from recoverai.domain import MerchantId, RevenueEvent
from recoverai.ingestion.exceptions import (
    DuplicateWebhookEvent,
    MalformedWebhookPayload,
)
from recoverai.ingestion.razorpay.normalizer import RazorpayNormalizer
from recoverai.ingestion.razorpay.signature import WebhookVerifier
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.exceptions import DuplicateEntityError
from recoverai.persistence.repositories.event import RevenueEventRepository

logger = logging.getLogger(__name__)


class WebhookIngestionService:
    """
    Coordinates the ingestion of a Razorpay webhook.
    Enforces signature validation, delegates normalization, and persists safely.
    """

    def __init__(
        self,
        verifier: WebhookVerifier,
        normalizer: RazorpayNormalizer,
        transaction_manager: TransactionManager,
    ):
        self.verifier = verifier
        self.normalizer = normalizer
        self.tm = transaction_manager

    def process_webhook(
        self,
        merchant_id: MerchantId,
        raw_body: bytes,
        signature: str | None,
        source_event_id: str | None,
        received_at: datetime,
    ) -> RevenueEvent | None:
        """
        Processes a webhook request completely.
        Returns the created RevenueEvent, or None if it was a duplicate.
        """
        # 1. Signature Verification (uses raw bytes before any JSON parsing)
        self.verifier.verify(raw_body, signature)
        logger.info(f"Webhook signature verified for event_id: {source_event_id}")

        # 2. Parse Payload
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook JSON: {e}")
            raise MalformedWebhookPayload("Invalid JSON body") from e

        # 3. Normalize
        event = self.normalizer.normalize(
            merchant_id, payload, source_event_id, received_at
        )
        logger.info(f"Normalized webhook to RevenueEvent {event.event_id}")

        # 4. Transactional Persistence and Deduplication
        try:
            with self.tm.transaction() as conn:
                repo = RevenueEventRepository(conn)
                repo.save(event)
        except DuplicateEntityError:
            # We treat duplicates as safe acknowledges, returning None
            logger.info(
                f"Duplicate webhook detected and ignored for source_event_id: {source_event_id}"
            )
            raise DuplicateWebhookEvent(f"Event {source_event_id} already ingested")

        return event
