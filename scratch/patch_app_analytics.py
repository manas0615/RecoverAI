import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

content = content.replace("import { AuditPage } from './pages/AuditPage';", "import { AuditPage } from './pages/AuditPage';\nimport { AnalyticsPage } from './pages/AnalyticsPage';")
content = content.replace('<Route path="/audit" element={<AuditPage />} />', '<Route path="/audit" element={<AuditPage />} />\n          <Route path="/analytics" element={<AnalyticsPage />} />')

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
