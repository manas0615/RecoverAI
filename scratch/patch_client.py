import re

with open('frontend/src/api/client.ts', 'r') as f:
    content = f.read()

content = content.replace("(/api/recovery-cases//abort", "(`/api/recovery-cases/${caseId}/abort`")

with open('frontend/src/api/client.ts', 'w') as f:
    f.write(content)
