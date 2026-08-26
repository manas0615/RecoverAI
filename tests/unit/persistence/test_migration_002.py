import pathlib
import sqlite3
from datetime import UTC, datetime

import pytest


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON;")
    yield c
    c.close()


def setup_data_for_v1(conn: sqlite3.Connection):
    conn.execute("BEGIN")
    # We must create the tables EXACTLY as they were in V1 before migrating
    conn.execute("""
        CREATE TABLE recovery_cases (
            case_id TEXT PRIMARY KEY,
            merchant_id TEXT NOT NULL,
            customer_id TEXT,
            revenue_source TEXT NOT NULL,
            amount_at_risk_minor INTEGER NOT NULL,
            amount_at_risk_currency TEXT NOT NULL,
            status TEXT NOT NULL,
            outcome_type TEXT,
            recovered_amount_minor INTEGER,
            recovered_amount_currency TEXT,
            opened_at TEXT NOT NULL,
            updated_at TEXT,
            closed_at TEXT
        );
    """)
    conn.execute("""
        CREATE TABLE recovery_actions (
            action_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
        );
    """)
    conn.execute("""
        CREATE TABLE intervention_plans (
            plan_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
        );
    """)
    conn.execute("""
        CREATE TABLE risk_assessments (
            assessment_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
        );
    """)

    # Insert cases
    dt = datetime.now(UTC).isoformat()

    # 1. Terminal / Closed Outcomes
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c1_rec', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'RECOVERED', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c1_not', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'NOT_RECOVERED', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c1_sup', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'SUPPRESSED', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c1_esc', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'ESCALATED', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c1_exp', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'EXPIRED', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c1_unk', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'UNKNOWN', ?)",
        (dt,),
    )

    # 2. Execution Unknown
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, opened_at) VALUES ('c2', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_actions (action_id, case_id, action_type, status, created_at) VALUES ('a2', 'c2', 'TYPE', 'EXECUTION_UNKNOWN', ?)",
        (dt,),
    )

    # 3. Verifying
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, opened_at) VALUES ('c3', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_actions (action_id, case_id, action_type, status, created_at) VALUES ('a3', 'c3', 'TYPE', 'VERIFICATION_PENDING', ?)",
        (dt,),
    )

    # 4. Executing
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, opened_at) VALUES ('c4', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_actions (action_id, case_id, action_type, status, created_at) VALUES ('a4', 'c4', 'TYPE', 'EXECUTING', ?)",
        (dt,),
    )

    # 5. Policy Review (PROPOSED)
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, opened_at) VALUES ('c5', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_actions (action_id, case_id, action_type, status, created_at) VALUES ('a5', 'c5', 'TYPE', 'PROPOSED', ?)",
        (dt,),
    )

    # 6. Assessed
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, opened_at) VALUES ('c6', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO risk_assessments (assessment_id, case_id) VALUES ('r6', 'c6')"
    )

    # 7. Detected Default
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, opened_at) VALUES ('c7', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', ?)",
        (dt,),
    )
    conn.execute("COMMIT")


def test_migration_002_success(conn: sqlite3.Connection):
    setup_data_for_v1(conn)

    migration_file = pathlib.Path(
        "recoverai/persistence/migrations/002_add_workflow_state.sql"
    )
    conn.executescript(migration_file.read_text())

    # Verify the data
    cur = conn.execute(
        "SELECT case_id, workflow_state, version FROM recovery_cases ORDER BY case_id"
    )
    rows = cur.fetchall()

    expected = {
        "c1_rec": "CLOSED",
        "c1_not": "CLOSED",
        "c1_sup": "CLOSED",
        "c1_esc": "CLOSED",
        "c1_exp": "CLOSED",
        "c1_unk": "CLOSED",
        "c2": "UNKNOWN",
        "c3": "VERIFYING",
        "c4": "EXECUTING",
        "c5": "POLICY_REVIEW",
        "c6": "ASSESSED",
        "c7": "DETECTED",
    }
    for row in rows:
        assert row["workflow_state"] == expected[row["case_id"]]
        assert row["version"] == 0


def test_migration_impossible_state_closed_executing(conn: sqlite3.Connection):
    setup_data_for_v1(conn)
    dt = datetime.now(UTC).isoformat()
    conn.execute("BEGIN")
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c_bad', 'm1', 'PAYMENT', 100, 'INR', 'CLOSED', 'RECOVERED', ?)",
        (dt,),
    )
    conn.execute(
        "INSERT INTO recovery_actions (action_id, case_id, action_type, status, created_at) VALUES ('a_bad', 'c_bad', 'TYPE', 'EXECUTING', ?)",
        (dt,),
    )
    conn.execute("COMMIT")

    migration_file = pathlib.Path(
        "recoverai/persistence/migrations/002_add_workflow_state.sql"
    )

    with pytest.raises(
        sqlite3.IntegrityError,
        match="Migration failed: Impossible historical state detected.",
    ):
        conn.executescript(migration_file.read_text())


def test_migration_impossible_state_open_with_outcome(conn: sqlite3.Connection):
    setup_data_for_v1(conn)
    dt = datetime.now(UTC).isoformat()
    conn.execute("BEGIN")
    conn.execute(
        "INSERT INTO recovery_cases (case_id, merchant_id, revenue_source, amount_at_risk_minor, amount_at_risk_currency, status, outcome_type, opened_at) VALUES ('c_bad', 'm1', 'PAYMENT', 100, 'INR', 'OPEN', 'RECOVERED', ?)",
        (dt,),
    )
    conn.execute("COMMIT")

    migration_file = pathlib.Path(
        "recoverai/persistence/migrations/002_add_workflow_state.sql"
    )

    with pytest.raises(
        sqlite3.IntegrityError,
        match="Migration failed: Impossible historical state detected.",
    ):
        conn.executescript(migration_file.read_text())
