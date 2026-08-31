import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

if 'ExecutionQueue' not in content:
    content = content.replace("import { ApprovalQueue } from './pages/ApprovalQueue';", "import { ApprovalQueue } from './pages/ApprovalQueue';\nimport { ExecutionQueue } from './pages/ExecutionQueue';")
    content = content.replace('<Route path="/approvals" element={<ApprovalQueue />} />', '<Route path="/approvals" element={<ApprovalQueue />} />\n          <Route path="/execution" element={<ExecutionQueue />} />')

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
