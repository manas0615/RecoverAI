import sqlite3
from pathlib import Path

import pytest

from recoverai.domain.audit import AuditActor, AuditEvent
from recoverai.persistence.repositories.audit import AuditRepository


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Run migrations manually on this connection
    migrations_dir = Path("recoverai/persistence/migrations")
    for mf in sorted(migrations_dir.glob("*.sql")):
        with open(mf, "r") as f:
            conn.executescript(f.read())
    yield conn
    conn.close()


def test_audit_event_creation():
    actor = AuditActor(type="POLICY_ENGINE", id="policy-1")
    evt = AuditEvent(
        event_type="POLICY_DECISION_CREATED",
        actor=actor,
        case_id="case_1",
        metadata={"reason": "test"},
    )
    assert evt.event_type == "POLICY_DECISION_CREATED"
    assert evt.actor.type == "POLICY_ENGINE"


def test_audit_redaction():
    actor = AuditActor(type="SYSTEM", id="sys-1")
    metadata = {
        "user_id": "123",
        "api_key": "sk-12345",
        "nested": {"token": "secret_token", "safe": "value"},
    }
    evt = AuditEvent(event_type="TEST", actor=actor, metadata=metadata)
    d = evt.to_dict()
    assert d["metadata"]["api_key"] == "***REDACTED***"
    assert d["metadata"]["nested"]["token"] == "***REDACTED***"
    assert d["metadata"]["nested"]["safe"] == "value"
    assert d["metadata"]["user_id"] == "123"


def test_audit_append_only(db_conn):
    repo = AuditRepository(db_conn)
    actor = AuditActor(type="SYSTEM", id="sys")

    evt1 = AuditEvent(
        event_type="STATE_TRANSITION",
        actor=actor,
        case_id="c1",
        previous_state="A",
        new_state="B",
    )
    repo.append(evt1)

    evt2 = AuditEvent(
        event_type="ACTION_EXECUTING", actor=actor, case_id="c1", action_id="a1"
    )
    repo.append(evt2)

    events = repo.get_by_case("c1")
    assert len(events) == 2
    assert events[0].event_type == "STATE_TRANSITION"
    assert events[1].event_type == "ACTION_EXECUTING"
    assert events[0].audit_event_id == evt1.audit_event_id


def test_audit_transaction_rollback(db_conn):
    repo = AuditRepository(db_conn)
    actor = AuditActor(type="SYSTEM", id="sys")

    try:
        # We manually simulate a rollback on the connection
        db_conn.execute("SAVEPOINT test_sp")
        repo.append(AuditEvent(event_type="SHOULD_ROLLBACK", actor=actor, case_id="c2"))
        raise ValueError("Simulated failure")
    except ValueError:
        db_conn.execute("ROLLBACK TO test_sp")

    events = repo.get_by_case("c2")
    assert len(events) == 0


def test_audit_policy_decision():
    actor = AuditActor(type="POLICY_ENGINE", id="policy-1")
    evt = AuditEvent(
        event_type="POLICY_DECISION_CREATED",
        actor=actor,
        decision_reference="pd_001",
        policy_version="1.2",
        metadata={"decision": "SUPPRESS", "matched_rules": ["SYSTEMIC_DEGRADATION"]},
    )
    assert evt.decision_reference == "pd_001"
    assert evt.metadata["decision"] == "SUPPRESS"


def test_audit_state_transition():
    actor = AuditActor(type="STATE_MACHINE", id="sm-1")
    evt = AuditEvent(
        event_type="RECOVERY_STATE_CHANGED",
        actor=actor,
        previous_state="POLICY_REVIEW",
        new_state="EXECUTING",
        case_id="case_1",
    )
    assert evt.previous_state == "POLICY_REVIEW"
    assert evt.new_state == "EXECUTING"


def test_audit_execution_result():
    actor = AuditActor(type="MCP_TOOL", id="create_payment_link")
    evt = AuditEvent(
        event_type="ACTION_EXECUTING",
        actor=actor,
        action_id="action_1",
        case_id="case_1",
    )
    assert evt.event_type == "ACTION_EXECUTING"
    assert evt.action_id == "action_1"


def test_audit_verification_result():
    actor = AuditActor(type="VERIFICATION", id="verify-1")
    evt = AuditEvent(
        event_type="VERIFICATION_COMPLETED",
        actor=actor,
        action_id="action_1",
        case_id="case_1",
        metadata={"outcome": "RECOVERED"},
    )
    assert evt.event_type == "VERIFICATION_COMPLETED"
    assert evt.metadata["outcome"] == "RECOVERED"


def test_audit_security_event():
    actor = AuditActor(type="RAZORPAY", id="webhook")
    evt = AuditEvent(
        event_type="WEBHOOK_SIGNATURE_REJECTED",
        actor=actor,
        metadata={"reason": "invalid_signature"},
    )
    assert evt.event_type == "WEBHOOK_SIGNATURE_REJECTED"


def test_audit_duplicate_idempotent():
    actor = AuditActor(type="RAZORPAY", id="webhook")
    evt = AuditEvent(
        event_type="WEBHOOK_DUPLICATE",
        actor=actor,
        metadata={"source_event_id": "evt_123"},
    )
    assert evt.event_type == "WEBHOOK_DUPLICATE"
    assert evt.metadata["source_event_id"] == "evt_123"


def test_audit_serialization_deserialization(db_conn):
    repo = AuditRepository(db_conn)
    actor = AuditActor(type="LLM_AGENT", id="gemini")
    evt = AuditEvent(
        event_type="LLM_RECOMMENDATION_CREATED",
        actor=actor,
        case_id="case_1",
        evidence_references=["evt_1", "risk_2"],
        metadata={"model": "gemini-2.5-pro"},
    )
    repo.append(evt)
    events = repo.get_by_case("case_1")
    assert len(events) == 1
    deser = events[0]
    assert deser.actor.type == "LLM_AGENT"
    assert deser.evidence_references == ["evt_1", "risk_2"]
    assert deser.metadata["model"] == "gemini-2.5-pro"
