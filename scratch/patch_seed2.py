import re

with open("scripts/seed_demo_data.py", "r", encoding="utf-8") as f:
    content = f.read()

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
    r'        case_e, t_e = create_base_case\(conn, "ESCALATION", 80000, 40\)\n(?:.*\n){1,60}        # SCENARIO F',
    patch_e + "\n        # SCENARIO F",
    content,
)

with open("scripts/seed_demo_data.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
