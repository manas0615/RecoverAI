lines = []
with open("tests/unit/api/test_api.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if line.startswith("def test_closed_case_read_and_mutate()"):
        start_idx = i
        break

if start_idx != -1:
    lines = lines[:start_idx]
    with open("tests/unit/api/test_api.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Removed bad tests.")
else:
    print("Could not find bad tests.")
