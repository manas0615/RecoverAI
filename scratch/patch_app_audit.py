import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

if 'AuditPage' not in content:
    content = content.replace(
        "import { VerificationQueue } from './pages/VerificationQueue';",
        "import { VerificationQueue } from './pages/VerificationQueue';\nimport { AuditPage } from './pages/AuditPage';"
    )
    content = content.replace(
        '<Route path="/verification" element={<VerificationQueue />} />',
        '<Route path="/verification" element={<VerificationQueue />} />\n          <Route path="/audit" element={<AuditPage />} />'
    )
    with open('frontend/src/App.tsx', 'w') as f:
        f.write(content)
