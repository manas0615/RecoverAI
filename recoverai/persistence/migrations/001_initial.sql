-- PRAGMA foreign_keys = ON; will be enforced at the connection level.



CREATE TABLE merchants (
    merchant_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    default_currency TEXT NOT NULL,
    status TEXT NOT NULL,
    external_reference TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    display_name TEXT,
    contact_reference TEXT,
    external_reference TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);

CREATE TABLE revenue_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_event_id TEXT,
    merchant_id TEXT NOT NULL,
    customer_id TEXT,
    amount_minor INTEGER,
    currency TEXT,
    external_reference TEXT,
    metadata JSON NOT NULL,
    schema_version TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    received_at TEXT NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
-- We use a partial index or COALESCE to ensure deduplication only when source_event_id is present.
-- SQLite UNIQUE considers NULLs distinct, but if source_event_id is NULL we might not want to enforce it.
-- We enforce source_type + source_event_id is unique if source_event_id is not null.
CREATE UNIQUE INDEX idx_revenue_events_source ON revenue_events(source_type, source_event_id) WHERE source_event_id IS NOT NULL;

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
    closed_at TEXT,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE case_source_events (
    case_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    PRIMARY KEY (case_id, event_id),
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES revenue_events(event_id)
);

CREATE TABLE risk_assessments (
    assessment_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    recovery_probability REAL NOT NULL,
    expected_recovery_minor INTEGER NOT NULL,
    expected_recovery_currency TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    feature_snapshot_reference TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
);

CREATE TABLE cause_assessments (
    cause_assessment_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    analysis_type TEXT NOT NULL,
    model_version TEXT NOT NULL,
    evidence_references_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
);

CREATE TABLE intervention_candidates (
    candidate_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    expected_recovery_probability REAL NOT NULL,
    expected_recovery_minor INTEGER NOT NULL,
    expected_recovery_currency TEXT NOT NULL,
    eligibility_status TEXT NOT NULL,
    intervention_cost_minor INTEGER,
    intervention_cost_currency TEXT,
    friction_score REAL,
    risk_score REAL,
    reason TEXT,
    evidence_references_json TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
);

CREATE TABLE intervention_plans (
    plan_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    selected_action_type TEXT,
    selection_reason TEXT NOT NULL,
    selection_model_version TEXT NOT NULL,
    expected_recovery_minor INTEGER,
    expected_recovery_currency TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
);

CREATE TABLE intervention_plan_candidates (
    plan_id TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    PRIMARY KEY (plan_id, candidate_id),
    FOREIGN KEY (plan_id) REFERENCES intervention_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES intervention_candidates(candidate_id)
);

CREATE TABLE policy_decisions (
    policy_decision_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    action_id_or_proposal_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    matched_rules_json TEXT NOT NULL,
    reason_codes_json TEXT NOT NULL,
    evaluated_at TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
);

CREATE TABLE recovery_actions (
    action_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    policy_decision_id TEXT,
    idempotency_key TEXT,
    workflow_execution_reference TEXT,
    external_reference TEXT,
    attempt_number INTEGER NOT NULL,
    status TEXT NOT NULL,
    failure_reason TEXT,
    requested_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id),
    FOREIGN KEY (policy_decision_id) REFERENCES policy_decisions(policy_decision_id)
);
-- Enforce uniqueness of idempotency keys globally if they exist to protect API calls
CREATE UNIQUE INDEX idx_recovery_actions_idempotency ON recovery_actions(idempotency_key) WHERE idempotency_key IS NOT NULL;
-- Enforce no concurrent overlapping actions for the same case and attempt number
CREATE UNIQUE INDEX idx_recovery_actions_case_attempt ON recovery_actions(case_id, action_type, attempt_number);

CREATE TABLE verification_records (
    verification_id TEXT PRIMARY KEY,
    action_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    verification_source TEXT NOT NULL,
    verified_state TEXT NOT NULL,
    external_reference TEXT,
    evidence_reference_json TEXT,
    checked_at TEXT NOT NULL,
    FOREIGN KEY (action_id) REFERENCES recovery_actions(action_id),
    FOREIGN KEY (case_id) REFERENCES recovery_cases(case_id)
);
