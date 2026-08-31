import re

with open('frontend/src/pages/CaseList.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'Showing {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, filteredCases.length)} of {filteredCases.length} cases',
    'Showing {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, filteredCases.length)} of {filteredCases.length} case{filteredCases.length !== 1 ? "s" : ""}'
)

with open('frontend/src/pages/CaseList.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
