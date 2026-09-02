import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_code = """        if latest_action.status in [ActionStatus.PROPOSED, ActionStatus.AUTHORIZED]:
            latest_action.status = ActionStatus.CANCELLED
            action_repo.update(latest_action)  # type: ignore
            conn.commit()"""

good_code = """        if latest_action.status in [ActionStatus.PROPOSED, ActionStatus.AUTHORIZED, ActionStatus.ESCALATED]:
            latest_action.status = ActionStatus.CANCELLED
            action_repo.update(latest_action)  # type: ignore
            
            from recoverai.persistence.repositories.audit import AuditRepository
            from recoverai.domain.audit import AuditEvent, AuditEventType, AuditActor, AuditActorType
            
            audit_repo = AuditRepository(conn)
            audit_repo.append(
                AuditEvent(
                    event_type=AuditEventType.ACTION_CANCELLED,
                    actor=AuditActor(type=AuditActorType.HUMAN, id="operator"),
                    case_id=latest_action.case_id,
                    action_id=latest_action.action_id,
                    metadata={"reason": "User aborted execution"}
                )
            )"""

if bad_code in content:
    content = content.replace(bad_code, good_code)
    with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed abort_execution to add audit event.")
else:
    print("Could not find the block in abort_execution.")
