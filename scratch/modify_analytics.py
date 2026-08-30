import sys

with open("recoverai/api/main.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '"outcome_distribution": outcome_distribution,' in line:
        new_lines.append(
            '            "outcomeDistribution": [{"name": k, "value": v} for k, v in outcome_distribution.items()],\n'
        )
    elif '"recovery_funnel": funnel,' in line:
        new_lines.append(
            '            "funnel": [{"stage": k.title(), "count": v} for k, v in funnel.items()],\n'
        )
    else:
        new_lines.append(line)

with open("recoverai/api/main.py", "w") as f:
    f.writelines(new_lines)
