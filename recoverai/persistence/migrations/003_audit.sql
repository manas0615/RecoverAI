CREATE TABLE IF NOT EXISTS audit_events (
    audit_event_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    case_id TEXT,
    action_id TEXT,
    decision_reference TEXT,
    policy_version TEXT,
    previous_state TEXT,
    new_state TEXT,
    evidence_references TEXT NOT NULL,
    metadata TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_case_id ON audit_events(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_action_id ON audit_events(action_id);
