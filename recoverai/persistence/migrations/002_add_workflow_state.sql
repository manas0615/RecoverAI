ALTER TABLE recovery_cases ADD COLUMN workflow_state TEXT;
ALTER TABLE recovery_cases ADD COLUMN version INTEGER NOT NULL DEFAULT 0;

CREATE TEMPORARY TRIGGER validate_migration
BEFORE UPDATE ON recovery_cases
FOR EACH ROW
WHEN (NEW.status = 'CLOSED' AND EXISTS (SELECT 1 FROM recovery_actions ra WHERE ra.case_id = NEW.case_id AND ra.status IN ('EXECUTING', 'PROPOSED', 'VERIFICATION_PENDING', 'EXECUTION_UNKNOWN')))
OR (NEW.status = 'CLOSED' AND NEW.outcome_type IS NULL)
OR (NEW.status = 'OPEN' AND NEW.outcome_type IS NOT NULL)
BEGIN
    SELECT RAISE(ABORT, 'Migration failed: Impossible historical state detected.');
END;

UPDATE recovery_cases
SET workflow_state = CASE
    WHEN status = 'CLOSED' THEN 'CLOSED'
    WHEN EXISTS (SELECT 1 FROM recovery_actions ra WHERE ra.case_id = recovery_cases.case_id AND ra.status = 'EXECUTION_UNKNOWN') THEN 'UNKNOWN'
    WHEN EXISTS (SELECT 1 FROM recovery_actions ra WHERE ra.case_id = recovery_cases.case_id AND ra.status = 'VERIFICATION_PENDING') THEN 'VERIFYING'
    WHEN EXISTS (SELECT 1 FROM recovery_actions ra WHERE ra.case_id = recovery_cases.case_id AND ra.status = 'EXECUTING') THEN 'EXECUTING'
    WHEN EXISTS (SELECT 1 FROM recovery_actions ra WHERE ra.case_id = recovery_cases.case_id AND ra.status = 'PROPOSED') THEN 'POLICY_REVIEW'
    WHEN EXISTS (SELECT 1 FROM intervention_plans ip WHERE ip.case_id = recovery_cases.case_id) THEN 'POLICY_REVIEW'
    WHEN EXISTS (SELECT 1 FROM risk_assessments rsa WHERE rsa.case_id = recovery_cases.case_id) THEN 'ASSESSED'
    ELSE 'DETECTED'
END;

DROP TRIGGER validate_migration;
