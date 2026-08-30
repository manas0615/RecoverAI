with open("scripts/seed_demo_data.py", "r", encoding="utf-8") as f:
    content = f.read()

target_b = """        add_audit(
            conn,
            AuditEventType.ACTION_EXECUTION_UNKNOWN,
            case_b.case_id,
            action_b.action_id,
            {"error": "Validation Error"},
            t_b + timedelta(minutes=2),
        )"""
replacement_b = """        add_audit(
            conn,
            AuditEventType.VERIFICATION_COMPLETED,
            case_b.case_id,
            action_b.action_id,
            {"new_state": "VERIFIED_FAILURE", "error": "Validation Error"},
            t_b + timedelta(minutes=2),
        )"""

content = content.replace(target_b, replacement_b)

target_c = """        action_c.failure_reason = "Timeout"
        action_repo.save(action_c)

        add_audit(conn, AuditEventType.CASE_CREATED, case_c.case_id, timestamp=t_c)"""
replacement_c = """        action_c.failure_reason = "Timeout"
        action_repo.save(action_c)

        case_c.advance_workflow(CaseWorkflowState.UNKNOWN, t_c + timedelta(minutes=2))
        case_repo.save(case_c)

        add_audit(conn, AuditEventType.CASE_CREATED, case_c.case_id, timestamp=t_c)"""

content = content.replace(target_c, replacement_c)

with open("scripts/seed_demo_data.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
