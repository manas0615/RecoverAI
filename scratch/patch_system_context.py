import re
with open('frontend/src/pages/CaseDetailView.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Available',
    '<div className="w-1.5 h-1.5 rounded-full bg-[var(--color-success)]"></div> Configured'
)

with open('frontend/src/pages/CaseDetailView.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
