class StateMachineError(Exception):
    """Base class for state machine errors."""


class InvalidTransitionError(StateMachineError):
    """Raised when an illegal state transition is attempted."""


class TerminalStateError(StateMachineError):
    """Raised when an operation is attempted on a closed case."""


class IdempotentEventError(StateMachineError):
    """Raised when an event has already been processed and can be safely ignored."""


class UnknownStateError(StateMachineError):
    """Raised when a blind retry is attempted on an EXECUTION_UNKNOWN action."""
