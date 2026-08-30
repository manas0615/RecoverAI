with open("recoverai/api/main.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # If we see the broken timeline def, we skip it
    if line.strip() == "@app.get(":
        if (
            i + 1 < len(lines)
            and '"/recovery-cases/{case_id}/timeline"' in lines[i + 1]
        ):
            skip = True
            continue

    if skip and line.strip().startswith('@app.get("/analytics"'):
        # Still skipping, this is the bad analytics
        continue

    if skip and line.strip().startswith(
        '@app.get("/recovery-cases/{case_id}/timeline"'
    ):
        # Reached the good timeline def, stop skipping
        skip = False

    if not skip:
        new_lines.append(line)

with open("recoverai/api/main.py", "w") as f:
    f.writelines(new_lines)
