import re
from pathlib import Path

file_path = Path("recoverai/api/main.py")
content = file_path.read_text(encoding="utf-8")

# 1. Patch `list_cases`
old_list_cases_end = """                cases.append(d)
                
        return {"cases": cases}"""

new_list_cases_end = """                # Fetch latest action details for execution monitoring
                from recoverai.persistence.repositories.action import RecoveryActionRepository
                action_repo = RecoveryActionRepository(conn)
                actions = action_repo.get_by_case(case_id_val)
                if actions:
                    latest_action = sorted(actions, key=lambda x: x.requested_at, reverse=True)[0]
                    d["action_type"] = latest_action.action_type.value
                    d["action_status"] = latest_action.status.value
                    d["action_id"] = latest_action.action_id.value
                    d["provider"] = latest_action.provider
                    d["external_reference"] = latest_action.external_reference
                else:
                    d["action_type"] = None
                    d["action_status"] = None
                    d["action_id"] = None
                    d["provider"] = None
                    d["external_reference"] = None

                cases.append(d)
                
        return {"cases": cases}"""

content = content.replace(old_list_cases_end, new_list_cases_end)

# 2. Patch `get_case`
old_get_case_end = """        # Find action_id for approval
        try:
            from recoverai.persistence.repositories.action import RecoveryActionRepository
            action_repo = RecoveryActionRepository(conn)
            cur = conn.execute("SELECT action_id FROM recovery_actions WHERE case_id = ? ORDER BY requested_at DESC LIMIT 1", (case_id,))
            row = cur.fetchone()
            if row:
                result["action_id"] = row["action_id"]
        except Exception:
            pass

        return result"""

new_get_case_end = """        # Find action details for execution UI
        try:
            from recoverai.persistence.repositories.action import RecoveryActionRepository
            action_repo = RecoveryActionRepository(conn)
            actions = action_repo.get_by_case(case_id)
            if actions:
                latest_action = sorted(actions, key=lambda x: x.requested_at, reverse=True)[0]
                result["action_type"] = latest_action.action_type.value
                result["action_status"] = latest_action.status.value
                result["action_id"] = latest_action.action_id.value
                result["provider"] = latest_action.provider
                result["external_reference"] = latest_action.external_reference
                result["action_requested_at"] = latest_action.requested_at.isoformat() if latest_action.requested_at else None
                result["action_executed_at"] = latest_action.executed_at.isoformat() if latest_action.executed_at else None
        except Exception:
            pass

        return result"""

content = content.replace(old_get_case_end, new_get_case_end)

# Add abort endpoint
abort_endpoint = """
@app.post("/recovery-cases/{case_id}/abort", dependencies=[Depends(require_frontend_key)])
def abort_execution(case_id: str):
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.action import RecoveryActionRepository
        from recoverai.domain.action import ActionStatus
        
        action_repo = RecoveryActionRepository(conn)
        actions = action_repo.get_by_case(case_id)
        if not actions:
            raise HTTPException(status_code=404, detail="No action found to abort")
            
        latest_action = sorted(actions, key=lambda x: x.requested_at, reverse=True)[0]
        
        if latest_action.status in [ActionStatus.PROPOSED, ActionStatus.AUTHORIZED, ActionStatus.EXECUTING]:
            latest_action.status = ActionStatus.CANCELLED
            action_repo.update(latest_action)
            conn.commit()
            return {"status": "success", "message": "Execution aborted"}
        else:
            raise HTTPException(status_code=400, detail="Cannot abort action in current state")
"""

if "def abort_execution(" not in content:
    content += abort_endpoint

file_path.write_text(content, encoding="utf-8")
print("Patched main.py")
