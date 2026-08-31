import re

with open('frontend/src/pages/ApprovalQueue.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Main wrapper: remove h-full, allow natural flow
content = content.replace(
    'max-w-[1440px] mx-auto animate-in fade-in duration-300 flex flex-col h-full',
    'max-w-[1440px] mx-auto animate-in fade-in duration-300 flex flex-col pb-8'
)

# 2. Split container: remove flex-1 min-h-0 so it doesn't force a flex height
content = content.replace(
    'flex flex-col lg:flex-row gap-6 flex-1 min-h-0',
    'flex flex-col lg:flex-row gap-6 items-start'
)

# 3. SelectedApprovalPanel wrapper: remove fixed height/scroll constraints
content = content.replace(
    'bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col h-full max-h-[800px] overflow-y-auto',
    'bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col'
)

# 4. Tighten internal panel padding
content = content.replace(
    'p-5 space-y-6',
    'p-4 space-y-4'
)

content = content.replace(
    'p-5 border-b',
    'p-4 border-b'
)

with open('frontend/src/pages/ApprovalQueue.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
