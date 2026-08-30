with open("scripts/seed_demo_data.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "case_b.close(RecoveryOutcomeValue.NOT_RECOVERED, None, t_b + timedelta(minutes=2))",
    "case_b.close(RecoveryOutcomeValue.NOT_RECOVERED, t_b + timedelta(minutes=2))",
)
content = content.replace(
    "case_d.close(RecoveryOutcomeValue.SUPPRESSED, None, t_d + timedelta(minutes=1))",
    "case_d.close(RecoveryOutcomeValue.SUPPRESSED, t_d + timedelta(minutes=1))",
)

with open("scripts/seed_demo_data.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
