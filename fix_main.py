with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "# Now execute it if it's not denied" in line:
        skip = True
        continue
    if skip:
        if "return {" in line:
            skip = False
        else:
            if "container.action_service.execute_action(action)" in line:
                new_lines.append(line)
            continue
    new_lines.append(line)

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Fixed duplicate if block")
