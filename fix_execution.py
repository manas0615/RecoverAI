with open("frontend/src/pages/ExecutionQueue.tsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "!['PROPOSED', 'AUTHORIZED'].includes(c.action_status || '')",
    "!['PROPOSED', 'AUTHORIZED', 'ESCALATED'].includes(c.action_status || '')"
)

with open("frontend/src/pages/ExecutionQueue.tsx", "w", encoding="utf-8") as f:
    f.write(content)
