class EventIngestionError(Exception):
    """Base class for all event ingestion errors."""


class InvalidWebhookSignature(EventIngestionError):
    """Raised when the webhook signature validation fails."""


class MalformedWebhookPayload(EventIngestionError):
    """Raised when the webhook payload is structurally invalid or missing required fields."""


class UnsupportedWebhookEvent(EventIngestionError):
    """Raised when the event type is valid JSON but not supported by the ingestion pipeline."""


class DuplicateWebhookEvent(EventIngestionError):
    """Raised when the event has already been ingested (based on source event ID)."""


class EventNormalizationError(EventIngestionError):
    """Raised when a specific event fails to normalize into a RevenueEvent."""
