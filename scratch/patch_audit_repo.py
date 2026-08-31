import re

with open('recoverai/persistence/repositories/audit.py', 'r') as f:
    content = f.read()

new_methods = '''
    def get_all(self, limit: int = 1000) -> list[AuditEvent]:
        cur = self.conn.execute(
            "SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        events = []
        for row in cur.fetchall():
            actor = AuditActor(
                type=AuditActorType(row["actor_type"]), id=row["actor_id"]
            )
            evt = AuditEvent(
                audit_event_id=row["audit_event_id"],
                timestamp=str_to_dt(row["timestamp"]) or datetime.now(UTC),
                event_type=AuditEventType(row["event_type"]),
                actor=actor,
                case_id=RecoveryCaseId(row["case_id"]) if row["case_id"] else None,
                action_id=RecoveryActionId(row["action_id"])
                if row["action_id"]
                else None,
                decision_reference=PolicyDecisionId(row["decision_reference"])
                if row["decision_reference"]
                else None,
                policy_version=row["policy_version"],
                previous_state=row["previous_state"],
                new_state=row["new_state"],
                evidence_references=[
                    EvidenceId(e) for e in json.loads(row["evidence_references"])
                ],
                metadata=json.loads(row["metadata"]),
            )
            events.append(evt)
        return events
'''

if "def get_all" not in content:
    content += new_methods
    with open('recoverai/persistence/repositories/audit.py', 'w') as f:
        f.write(content)
