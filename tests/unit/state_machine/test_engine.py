import os
import tempfile
from datetime import UTC, datetime

import pytest

from recoverai.domain.case import (
    CaseWorkflowState,
    RecoveryCase,
    RecoveryCaseStatus,
    RecoveryOutcomeValue,
    RevenueSource,
)
from recoverai.domain.identifiers import MerchantId, RecoveryCaseId, RevenueEventId
from recoverai.domain.money import CurrencyCode, Money, RevenueAmount
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.case import RecoveryCaseRepository
from recoverai.state_machine.commands import CloseCaseCommand
from recoverai.state_machine.engine import RecoveryStateMachine
from recoverai.state_machine.exceptions import (
    InvalidTransitionError,
    TerminalStateError,
    UnknownStateError,
)


@pytest.fixture
def tm():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    manager = TransactionManager(f"sqlite:///{path}")
    manager.run_migrations()
    yield manager
    os.unlink(path)


def setup_dummy_merchant_and_case(tm: TransactionManager) -> RecoveryCaseId:
    with tm.transaction() as conn:
        conn.execute(
            "INSERT INTO merchants (merchant_id, external_reference, display_name, status, default_currency, created_at, updated_at) VALUES ('merch_1', 'ext', 'name', 'ACTIVE', 'INR', '2026-08-26T00:00:00+00:00', '2026-08-26T00:00:00+00:00')"
        )
        conn.execute(
            "INSERT INTO revenue_events (event_id, event_type, source_type, merchant_id, metadata, schema_version, occurred_at, received_at) VALUES ('evt_1', 'PAYMENT_FAILED', 'API', 'merch_1', '{}', '1.0', '2026-08-26T00:00:00+00:00', '2026-08-26T00:00:00+00:00')"
        )

        repo = RecoveryCaseRepository(conn)
        case_id = RecoveryCaseId("case_1")
        case = RecoveryCase(
            case_id=case_id,
            merchant_id=MerchantId("merch_1"),
            revenue_source=RevenueSource.PAYMENT,
            amount_at_risk=RevenueAmount(Money(100, CurrencyCode.INR)),
            opened_at=datetime.now(UTC),
            source_event_ids={RevenueEventId("evt_1")},
        )
        repo.save(case)
        return case_id


def test_valid_transitions(tm):
    case_id = setup_dummy_merchant_and_case(tm)
    engine = RecoveryStateMachine(tm)

    dt = datetime.now(UTC)

    # DETECTED -> ENRICHING
    engine.advance_workflow(case_id.value, CaseWorkflowState.ENRICHING, dt)

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        case = repo.get(case_id)
        assert case.workflow_state == CaseWorkflowState.ENRICHING
        assert case.version == 1

    # ENRICHING -> ASSESSED
    engine.advance_workflow(case_id.value, CaseWorkflowState.ASSESSED, dt)

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        case = repo.get(case_id)
        assert case.workflow_state == CaseWorkflowState.ASSESSED
        assert case.version == 2


def test_idempotent_event(tm):
    case_id = setup_dummy_merchant_and_case(tm)
    engine = RecoveryStateMachine(tm)
    dt = datetime.now(UTC)

    # DETECTED -> ENRICHING
    engine.advance_workflow(case_id.value, CaseWorkflowState.ENRICHING, dt)

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        assert repo.get(case_id).version == 1

    # Idempotent call
    engine.advance_workflow(case_id.value, CaseWorkflowState.ENRICHING, dt)

    # Version shouldn't change
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        assert repo.get(case_id).version == 1


def test_invalid_transition(tm):
    case_id = setup_dummy_merchant_and_case(tm)
    engine = RecoveryStateMachine(tm)
    dt = datetime.now(UTC)

    # DETECTED -> EXECUTING (Invalid)
    with pytest.raises(InvalidTransitionError):
        engine.advance_workflow(case_id.value, CaseWorkflowState.EXECUTING, dt)


def test_unknown_state_blind_retry_fails(tm):
    case_id = setup_dummy_merchant_and_case(tm)
    engine = RecoveryStateMachine(tm)
    dt = datetime.now(UTC)

    # DETECTED -> ENRICHING -> UNKNOWN
    engine.advance_workflow(case_id.value, CaseWorkflowState.ENRICHING, dt)
    engine.advance_workflow(case_id.value, CaseWorkflowState.UNKNOWN, dt)

    # UNKNOWN -> EXECUTING (Blind retry - Invalid per domain rules)
    with pytest.raises(UnknownStateError):
        engine.advance_workflow(case_id.value, CaseWorkflowState.EXECUTING, dt)


def test_terminal_state_protection(tm):
    case_id = setup_dummy_merchant_and_case(tm)
    engine = RecoveryStateMachine(tm)
    dt = datetime.now(UTC)

    cmd = CloseCaseCommand(
        case_id=case_id, outcome=RecoveryOutcomeValue.SUPPRESSED, timestamp=dt
    )
    engine.close_case(cmd)

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        case = repo.get(case_id)
        assert case.status == RecoveryCaseStatus.CLOSED
        assert case.workflow_state == CaseWorkflowState.CLOSED
        assert case.outcome_type == RecoveryOutcomeValue.SUPPRESSED
        assert case.version == 1

    # Try advancing after CLOSED
    with pytest.raises(TerminalStateError):
        engine.advance_workflow(case_id.value, CaseWorkflowState.ENRICHING, dt)

    # Try closing again with DIFFERENT outcome
    cmd2 = CloseCaseCommand(
        case_id=case_id, outcome=RecoveryOutcomeValue.ESCALATED, timestamp=dt
    )
    with pytest.raises(TerminalStateError):
        engine.close_case(cmd2)

    # Idempotent close does not raise
    engine.close_case(cmd)

    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        case = repo.get(case_id)
        assert case.version == 1  # unchanged


def test_transaction_rollback(tm):
    """
    Shows an actual failure test proving:
    state mutation A + related persistence mutation B + B fails = A rolled back
    using the real P03 TransactionManager.
    """
    case_id = setup_dummy_merchant_and_case(tm)
    dt = datetime.now(UTC)

    with pytest.raises(Exception):
        with tm.transaction() as conn:
            repo = RecoveryCaseRepository(conn)
            case = repo.get(case_id)

            # State mutation A
            case.advance_workflow(CaseWorkflowState.ENRICHING, dt)
            repo.save(case)

            # Related persistence mutation B fails
            conn.execute(
                "INSERT INTO recovery_cases (case_id) VALUES ('invalid')"
            )  # Violates NOT NULL constraints

    # Assert A rolled back
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        case = repo.get(case_id)
        assert case.workflow_state == CaseWorkflowState.DETECTED
        assert case.version == 0
