import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

if 'VerificationQueue' not in content:
    content = content.replace("import { ExecutionQueue } from './pages/ExecutionQueue';", "import { ExecutionQueue } from './pages/ExecutionQueue';\nimport { VerificationQueue } from './pages/VerificationQueue';")
    content = content.replace('<Route path="/execution" element={<ExecutionQueue />} />', '<Route path="/execution" element={<ExecutionQueue />} />\n          <Route path="/verification" element={<VerificationQueue />} />')

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
