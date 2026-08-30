with open("scripts/seed_demo_data.py", "r", encoding="utf-8") as f:
    content = f.read()

# For case_b:
target_b = """        action_b.record_verification(
            ActionStatus.VERIFIED_FAILURE, t_b + timedelta(minutes=2)
        )
        action_b.failure_reason = "Validation Error"
        action_repo.save(action_b)

        add_audit(conn, AuditEventType.CASE_CREATED, case_b.case_id, timestamp=t_b)"""
replacement_b = """        action_b.record_verification(
            ActionStatus.VERIFIED_FAILURE, t_b + timedelta(minutes=2)
        )
        action_b.failure_reason = "Validation Error"
        action_repo.save(action_b)
        
        case_b.advance_workflow(CaseWorkflowState.VERIFYING, t_b + timedelta(minutes=1, seconds=30))
        case_b.close(RecoveryOutcomeValue.NOT_RECOVERED, t_b + timedelta(minutes=2))
        case_repo.save(case_b)

        add_audit(conn, AuditEventType.CASE_CREATED, case_b.case_id, timestamp=t_b)"""

if target_b in content:
    content = content.replace(target_b, replacement_b)
else:
    print("Failed to replace B")

with open("scripts/seed_demo_data.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
