import re

with open("scripts/seed_demo_data.py", "r") as f:
    content = f.read()

# SCENARIO B: Add case state update and correct audit events
patch_b = """
        action_repo.save(action_b)

        case_b.advance_workflow(CaseWorkflowState.VERIFYING, t_b + timedelta(minutes=1, seconds=30))
        case_b.close(RecoveryOutcomeValue.NOT_RECOVERED, None, t_b + timedelta(minutes=2))
        case_repo.save(case_b)

        add_audit(conn, AuditEventType.CASE_CREATED, case_b.case_id, timestamp=t_b)
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_b.case_id,
            action_b.action_id,
            {"decision": "APPROVE"},
            t_b + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.VERIFICATION_COMPLETED,
            case_b.case_id,
            action_b.action_id,
            {"new_state": "VERIFIED_FAILURE", "error": "Validation Error"},
            t_b + timedelta(minutes=2),
        )
"""
content = re.sub(
    r"        action_repo\.save\(action_b\)\n\n        add_audit\(conn, AuditEventType\.CASE_CREATED, case_b\.case_id, timestamp=t_b\)\n(?:.*\n){1,15}        # SCENARIO C",
    patch_b + "\n        # SCENARIO C",
    content,
)

# SCENARIO C: Add case state update
patch_c = """
        action_repo.save(action_c)

        case_c.advance_workflow(CaseWorkflowState.UNKNOWN, t_c + timedelta(minutes=2))
        case_repo.save(case_c)

        add_audit(conn, AuditEventType.CASE_CREATED, case_c.case_id, timestamp=t_c)
        add_audit(
            conn,
            AuditEventType.RECOVERY_STATE_CHANGED,
            case_c.case_id,
            action_c.action_id,
            {"new_state": "UNKNOWN"},
            t_c + timedelta(minutes=2),
        )
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_c.case_id,
            action_c.action_id,
            {"decision": "APPROVE"},
            t_c + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.ACTION_EXECUTION_UNKNOWN,
            case_c.case_id,
            action_c.action_id,
            {"error": "Timeout"},
            t_c + timedelta(minutes=2),
        )
"""
content = re.sub(
    r"        action_repo\.save\(action_c\)\n\n        add_audit\(conn, AuditEventType\.CASE_CREATED, case_c\.case_id, timestamp=t_c\)\n(?:.*\n){1,25}        # SCENARIO D",
    patch_c + "\n        # SCENARIO D",
    content,
)

# SCENARIO D: Add case state update
patch_d = """
        action_repo.save(action_d)

        case_d.close(RecoveryOutcomeValue.SUPPRESSED, None, t_d + timedelta(minutes=1))
        case_repo.save(case_d)

        conn.execute(
"""
content = re.sub(
    r"        action_repo\.save\(action_d\)\n\n        conn\.execute\(",
    patch_d,
    content,
)

# SCENARIO E: Remove begin_execution, record_verification, modify audit events
patch_e = """
        case_e, t_e = create_base_case(conn, "ESCALATION", 80000, 40)
        action_e = RecoveryAction(
            action_id=RecoveryActionId("act_ESCALATION"),
            case_id=case_e.case_id,
            action_type=ActionType.CREATE_PAYMENT_LINK,
            status=ActionStatus.PROPOSED,
            requested_at=t_e,
        )
        
        # Policy escalates it
        conn.execute(
            \"\"\"INSERT INTO policy_decisions (policy_decision_id, case_id, action_id_or_proposal_id, decision, policy_version, matched_rules_json, reason_codes_json, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)\"\"\",
            (
                "dec_ESCALATE",
                case_e.case_id.value,
                action_e.action_id.value,
                "ESCALATE",
                "1.0",
                "[]",
                "[]",
                t_e.isoformat(),
            ),
        )
        # It stays proposed/escalated, no execution yet
        action_repo.save(action_e)

        case_e.advance_workflow(
            CaseWorkflowState.WAITING_APPROVAL, t_e + timedelta(minutes=1)
        )
        case_repo.save(case_e)

        add_audit(conn, AuditEventType.CASE_CREATED, case_e.case_id, timestamp=t_e)
        add_audit(
            conn,
            AuditEventType.RECOVERY_STATE_CHANGED,
            case_e.case_id,
            action_e.action_id,
            {"new_state": "WAITING_APPROVAL"},
            t_e + timedelta(minutes=1, seconds=30),
        )
        add_audit(
            conn,
            AuditEventType.POLICY_DECISION_CREATED,
            case_e.case_id,
            action_e.action_id,
            {"decision": "ESCALATE", "reason": "HIGH_VALUE_ACTION"},
            t_e + timedelta(minutes=1),
        )
        add_audit(
            conn,
            AuditEventType.CASE_ESCALATED,
            case_e.case_id,
            action_e.action_id,
            timestamp=t_e + timedelta(minutes=1),
        )
"""
content = re.sub(
    r'        case_e, t_e = create_base_case\(conn, "ESCALATION", 80000, 40\)\n(?:.*\n){1,50}        # SCENARIO F',
    patch_e + "\n        # SCENARIO F",
    content,
)

with open("scripts/seed_demo_data.py", "w") as f:
    f.write(content)
print("done")
