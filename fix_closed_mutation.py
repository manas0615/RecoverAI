import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

closed_check = """
        if case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")
"""

# 1. analyze_case
analyze_block = """        if not case:
            raise HTTPException(status_code=404, detail="Case not found")"""

if analyze_block in content:
    content = content.replace(analyze_block, analyze_block + closed_check)

# 2. approve_action
approve_block = """        case = case_repo.get(RecoveryCaseId(case_id))
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")"""
if approve_block in content:
    content = content.replace(approve_block, approve_block + closed_check)

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Added closed case checks to analyze_case and approve_action")
