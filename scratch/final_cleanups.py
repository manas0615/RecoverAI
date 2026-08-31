import re

with open('frontend/src/types/domain.ts', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s+workflow_state\?: string;', '\n  workflow_state?: string;\n  failure_code?: string;\n  recommendation?: string;\n  updated_at?: string;', content)

with open('frontend/src/types/domain.ts', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated domain.ts")

# Also remove unused imports in CaseList and CaseTable
with open('frontend/src/pages/CaseList.tsx', 'r', encoding='utf-8') as f:
    cl = f.read()
cl = cl.replace('AlertTriangle, Clock, PlayCircle, RefreshCw, Filter, Download, Search, ChevronLeft, ChevronRight', 'AlertTriangle, RefreshCw, Filter, Download, Search')
with open('frontend/src/pages/CaseList.tsx', 'w', encoding='utf-8') as f:
    f.write(cl)

with open('frontend/src/components/data-display/CaseTable.tsx', 'r', encoding='utf-8') as f:
    ct = f.read()
ct = ct.replace('ChevronRight, Inbox', 'Inbox')
with open('frontend/src/components/data-display/CaseTable.tsx', 'w', encoding='utf-8') as f:
    f.write(ct)
