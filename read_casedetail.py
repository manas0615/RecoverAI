with open("frontend/src/pages/CaseDetailView.tsx", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "Execution" in line or "action" in line.lower() or "reference" in line.lower():
        print(f"{i}: {line.strip()}")
