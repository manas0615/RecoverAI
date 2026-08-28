import json
import sqlite3
from datetime import UTC, datetime

from recoverai.domain.audit import AuditActor, AuditEvent
from recoverai.persistence.mappers import str_to_dt


class AuditRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def append(self, event: AuditEvent) -> None:
        row = event.to_dict()
        # Ensure append-only
        self.conn.execute(
            """
            INSERT INTO audit_events (
                audit_event_id, timestamp, event_type, actor_type, actor_id,
                case_id, action_id, decision_reference, policy_version,
                previous_state, new_state, evidence_references, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["audit_event_id"],
                row["timestamp"],
                row["event_type"],
                row["actor"]["type"],
                row["actor"]["id"],
                row["case_id"],
                row["action_id"],
                row["decision_reference"],
                row["policy_version"],
                row["previous_state"],
                row["new_state"],
                json.dumps(row["evidence_references"]),
                json.dumps(row["metadata"]),
            ),
        )

    def get_by_case(self, case_id: str) -> list[AuditEvent]:
        cur = self.conn.execute(
            "SELECT * FROM audit_events WHERE case_id = ? ORDER BY timestamp ASC",
            (case_id,),
        )
        events = []
        for row in cur.fetchall():
            actor = AuditActor(type=row["actor_type"], id=row["actor_id"])
            evt = AuditEvent(
                audit_event_id=row["audit_event_id"],
                timestamp=str_to_dt(row["timestamp"]) or datetime.now(UTC),
                event_type=row["event_type"],
                actor=actor,
                case_id=row["case_id"],
                action_id=row["action_id"],
                decision_reference=row["decision_reference"],
                policy_version=row["policy_version"],
                previous_state=row["previous_state"],
                new_state=row["new_state"],
                evidence_references=json.loads(row["evidence_references"]),
                metadata=json.loads(row["metadata"]),
            )
            events.append(evt)
        return events
