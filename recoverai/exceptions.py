class RecoverAIException(Exception):
    """Base exception for all RecoverAI custom exceptions."""


class ConfigurationError(RecoverAIException):
    """Raised when there is an issue with the application configuration or startup."""


class ValidationError(RecoverAIException):
    """Raised when domain or application validation fails."""


class InternalError(RecoverAIException):
    """Raised when an unexpected or internal system error occurs."""
