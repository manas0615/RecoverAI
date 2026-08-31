import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

old_part = """        result = case_to_dict(case)
        result["events"] = [
            {"""

new_part = """        audit_events = audit_repo.get_by_case(case_id)
        result = case_to_dict(case)
        result["timeline"] = [e.to_dict() for e in audit_events]
        result["events"] = [
            {"""

if 'result["timeline"]' not in content:
    content = content.replace(old_part, new_part)
    with open('recoverai/api/main.py', 'w') as f:
        f.write(content)
