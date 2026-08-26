import logging
from datetime import datetime

from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCaseStatus,
)
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.state_machine.commands import (
    CloseCaseCommand,
)
from recoverai.state_machine.exceptions import (
    IdempotentEventError,
    InvalidTransitionError,
    TerminalStateError,
    UnknownStateError,
)

logger = logging.getLogger(__name__)

# Define the legal state transitions for CaseWorkflowState
# A dictionary mapping from a state to a set of allowed next states.
ALLOWED_TRANSITIONS: dict[CaseWorkflowState, set[CaseWorkflowState]] = {
    CaseWorkflowState.DETECTED: {
        CaseWorkflowState.ENRICHING,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.ENRICHING: {
        CaseWorkflowState.ASSESSED,
        CaseWorkflowState.UNKNOWN,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.ASSESSED: {
        CaseWorkflowState.PLANNING,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.PLANNING: {
        CaseWorkflowState.POLICY_REVIEW,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.POLICY_REVIEW: {
        CaseWorkflowState.WAITING_APPROVAL,
        CaseWorkflowState.EXECUTING,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.WAITING_APPROVAL: {
        CaseWorkflowState.EXECUTING,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.EXECUTING: {
        CaseWorkflowState.VERIFYING,
        CaseWorkflowState.UNKNOWN,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.VERIFYING: {
        CaseWorkflowState.EXECUTING,
        CaseWorkflowState.UNKNOWN,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.UNKNOWN: {
        CaseWorkflowState.VERIFYING,
        CaseWorkflowState.CLOSED,
    },
    CaseWorkflowState.CLOSED: set(),  # Terminal state
}


class RecoveryStateMachine:
    """
    Core state machine engine for RecoveryCase.
    Enforces legal transitions, idempotent execution, and atomicity.
    """

    def __init__(self, tm: TransactionManager):
        self.tm = tm

    def _validate_transition(
        self, current: CaseWorkflowState, next_state: CaseWorkflowState
    ) -> None:
        """Validates if transitioning from `current` to `next_state` is allowed."""
        if current == next_state:
            # Idempotent state transition (e.g. out of order duplicate event for the exact same state)
            raise IdempotentEventError(
                f"Idempotent transition to same state: {current.name}"
            )

        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if next_state not in allowed:
            raise InvalidTransitionError(
                f"Illegal transition from {current.name} to {next_state.name}"
            )

    def advance_workflow(
        self, case_id_str: str, next_state: CaseWorkflowState, timestamp: datetime
    ) -> None:
        """
        Advances the granular workflow state of a case.
        """
        with self.tm.transaction() as conn:
            repo = RecoveryCaseRepository(conn)
            from recoverai.domain.identifiers import RecoveryCaseId

            case = repo.get(RecoveryCaseId(case_id_str))

            if not case:
                raise ValueError(f"Case {case_id_str} not found")

            if case.status == RecoveryCaseStatus.CLOSED:
                raise TerminalStateError(f"Case {case_id_str} is already CLOSED.")

            # If attempting to execute from an UNKNOWN state blindly
            if (
                case.workflow_state == CaseWorkflowState.UNKNOWN
                and next_state == CaseWorkflowState.EXECUTING
            ):
                raise UnknownStateError(
                    f"Cannot blindly retry from UNKNOWN state for case {case_id_str}"
                )

            try:
                self._validate_transition(case.workflow_state, next_state)
            except IdempotentEventError:
                logger.info(f"Idempotent transition ignored for {case_id_str}")
                return

            case.advance_workflow(next_state, timestamp)
            repo.save(case)

    def close_case(self, cmd: CloseCaseCommand) -> None:
        """
        Closes a RecoveryCase with a terminal outcome.
        """
        with self.tm.transaction() as conn:
            repo = RecoveryCaseRepository(conn)
            case = repo.get(cmd.case_id)

            if not case:
                raise ValueError(f"Case {cmd.case_id.value} not found")

            if case.status == RecoveryCaseStatus.CLOSED:
                if case.outcome_type == cmd.outcome:
                    logger.info(f"Idempotent close ignored for {cmd.case_id.value}")
                    return
                raise TerminalStateError(
                    f"Case {cmd.case_id.value} is already CLOSED with a different outcome."
                )

            try:
                self._validate_transition(case.workflow_state, CaseWorkflowState.CLOSED)
            except IdempotentEventError:
                # Should be caught by the CLOSED check above, but just in case
                return

            case.close(cmd.outcome, cmd.timestamp, cmd.recovered_amount)
            repo.save(case)
