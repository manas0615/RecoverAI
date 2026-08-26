import os
import tempfile
from datetime import UTC, datetime

import pytest

from recoverai.domain import (
    CaseWorkflowState,
    CurrencyCode,
    MerchantId,
    Money,
    RecoveryCase,
    RecoveryCaseId,
    RevenueAmount,
    RevenueEventId,
    RevenueSource,
)
from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.exceptions import StaleStateTransitionError
from recoverai.persistence.repositories.case import RecoveryCaseRepository


@pytest.fixture
def tm():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    manager = TransactionManager(f"sqlite:///{path}")
    manager.run_migrations()
    yield manager
    os.unlink(path)


@pytest.fixture
def repo(tm):
    with tm.transaction() as conn:
        return RecoveryCaseRepository(conn)


def create_dummy_case(case_id: str) -> RecoveryCase:
    return RecoveryCase(
        case_id=RecoveryCaseId(case_id),
        merchant_id=MerchantId("merch_1"),
        revenue_source=RevenueSource.PAYMENT,
        amount_at_risk=RevenueAmount(Money(100, CurrencyCode.INR)),
        opened_at=datetime.now(UTC),
        source_event_ids={RevenueEventId("evt_1")},
    )


def setup_dummy_merchant(tm):
    with tm.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO merchants (merchant_id, external_reference, display_name, status, default_currency, created_at, updated_at) VALUES ('merch_1', 'ext', 'name', 'ACTIVE', 'INR', '2026-08-26T00:00:00+00:00', '2026-08-26T00:00:00+00:00')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO revenue_events (event_id, event_type, source_type, merchant_id, metadata, schema_version, occurred_at, received_at) VALUES ('evt_1', 'PAYMENT_FAILED', 'API', 'merch_1', '{}', '1.0', '2026-08-26T00:00:00+00:00', '2026-08-26T00:00:00+00:00')"
        )


def test_initial_version_is_0(tm, repo):
    setup_dummy_merchant(tm)
    case = create_dummy_case("case_v1")
    assert case.version == 0
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        repo.save(case)

    with tm.transaction() as conn:
        repo2 = RecoveryCaseRepository(conn)
        loaded = repo2.get(RecoveryCaseId("case_v1"))
        assert loaded is not None
        assert loaded.version == 0


def test_successful_update_increments_version(tm):
    setup_dummy_merchant(tm)
    case = create_dummy_case("case_v2")
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        repo.save(case)

    # Modify and save
    case.workflow_state = CaseWorkflowState.ASSESSED
    case.updated_at = datetime.now(UTC)
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        repo.save(case)

    assert case.version == 1

    with tm.transaction() as conn:
        repo2 = RecoveryCaseRepository(conn)
        loaded = repo2.get(RecoveryCaseId("case_v2"))
        assert loaded is not None
        assert loaded.version == 1
        assert loaded.workflow_state == CaseWorkflowState.ASSESSED

    # Modify again
    loaded.workflow_state = CaseWorkflowState.EXECUTING
    with tm.transaction() as conn:
        repo3 = RecoveryCaseRepository(conn)
        repo3.save(loaded)

    assert loaded.version == 2


def test_stale_update_fails(tm):
    setup_dummy_merchant(tm)
    case = create_dummy_case("case_v3")
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        repo.save(case)

    # Worker A fetches
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        worker_a_case = repo.get(RecoveryCaseId("case_v3"))

    # Worker B fetches, modifies, and saves
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        worker_b_case = repo.get(RecoveryCaseId("case_v3"))
        worker_b_case.workflow_state = CaseWorkflowState.ASSESSED
        repo.save(worker_b_case)

    # Worker A attempts to save stale data
    worker_a_case.workflow_state = CaseWorkflowState.VERIFYING

    with pytest.raises(
        StaleStateTransitionError,
        match="Stale update for RecoveryCase case_v3. Expected version 0.",
    ):
        with tm.transaction() as conn:
            repo = RecoveryCaseRepository(conn)
            repo.save(worker_a_case)

    # Ensure no data was partially written by Worker A
    with tm.transaction() as conn:
        repo = RecoveryCaseRepository(conn)
        final_case = repo.get(RecoveryCaseId("case_v3"))
        assert final_case.version == 1
        assert final_case.workflow_state == CaseWorkflowState.ASSESSED
