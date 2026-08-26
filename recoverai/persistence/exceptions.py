class PersistenceError(Exception):
    """Base class for all persistence exceptions."""


class ConcurrencyError(PersistenceError):
    """Raised when an update fails due to conditional (stale) data."""


class EntityNotFoundError(PersistenceError):
    """Raised when an expected entity does not exist in the database."""


class DuplicateEntityError(PersistenceError):
    """Raised when a unique constraint is violated."""


class StaleStateTransitionError(ConcurrencyError):
    """Raised when an optimistic locking check fails on RecoveryCase update."""
