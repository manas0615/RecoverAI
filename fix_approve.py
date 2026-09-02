import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_approve = """def approve_action(case_id: str, action_id: str):
    try:"""

good_approve = """def approve_action(case_id: str, action_id: str):
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.case import RecoveryCaseRepository
        case = RecoveryCaseRepository(conn).get(RecoveryCaseId(case_id))
        if case and case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")
    try:"""

if bad_approve in content:
    content = content.replace(bad_approve, good_approve)
    with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added closed check to approve_action.")
else:
    print("Could not find approve_action.")
