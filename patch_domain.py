import re

with open("frontend/src/types/domain.ts", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("external_reference?: string;", "external_reference?: string;\n  workflow_execution_reference?: string;")

with open("frontend/src/types/domain.ts", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated domain.ts")
