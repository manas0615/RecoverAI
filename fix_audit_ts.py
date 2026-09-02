with open("frontend/src/pages/AuditPage.tsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(".map((e, i) => (", ".map((e) => (")

with open("frontend/src/pages/AuditPage.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed AuditPage.tsx")
