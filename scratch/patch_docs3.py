import os

failure_path = "docs/reports/package-25/failure_analysis.md"
with open(failure_path, "r", encoding="utf-8") as f:
    fail_content = f.read()

fail_content = fail_content.replace(
    "risks severe customer churn and friction",
    "recognizes customer friction is a motivating product concern"
)
with open(failure_path, "w", encoding="utf-8") as f:
    f.write(fail_content)

rob_path = "docs/reports/package-25/robustness_analysis.md"
with open(rob_path, "r", encoding="utf-8") as f:
    rob_content = f.read()
rob_content = rob_content.replace("saving your customer relationships", "avoiding failed interventions")
with open(rob_path, "w", encoding="utf-8") as f:
    f.write(rob_content)
