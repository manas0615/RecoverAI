import re

with open('frontend/src/pages/CaseDetailView.tsx', 'r') as f:
    content = f.read()

content = content.replace('mb-6">Lifecycle</h2>', 'mb-6">Recovery Case Timeline</h2>')

with open('frontend/src/pages/CaseDetailView.tsx', 'w') as f:
    f.write(content)
