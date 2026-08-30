with open("tests/unit/api/test_api.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'assert "outcome_distribution" in data' in line:
        new_lines.append('    assert "outcomeDistribution" in data\n')
    elif 'assert "recovery_funnel" in data' in line:
        new_lines.append('    assert "funnel" in data\n')
    else:
        new_lines.append(line)

with open("tests/unit/api/test_api.py", "w") as f:
    f.writelines(new_lines)
