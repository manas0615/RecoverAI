with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "container.action_service.execute_action(action)" in line:
        lines[i] = "            container.action_service.execute_action(action)\n"

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Fixed indentation")
