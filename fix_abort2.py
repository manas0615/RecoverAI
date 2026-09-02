import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_code = "actions = action_repo.get_by_case(case_id)  # type: ignore"
good_code = "actions = action_repo.get_by_case(RecoveryCaseId(case_id))"

if bad_code in content:
    content = content.replace(bad_code, good_code)
    with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed abort_execution case_id.")
else:
    print("Could not find block.")
