import os
import re

interp_path = "docs/reports/package-25/benchmark_interpretation.md"
with open(interp_path, "r", encoding="utf-8") as f:
    interp_content = f.read()
interp_content = interp_content.replace(
    "However, RecoverAI wins the product race: it provides a tunable mechanism",
    "However, RecoverAI prioritizes intervention precision and controlled escalation, accepting some gross-recovery loss in exchange for fewer failed interventions. It provides a tunable mechanism"
)
with open(interp_path, "w", encoding="utf-8") as f:
    f.write(interp_content)
