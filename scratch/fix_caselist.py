import re

with open('frontend/src/pages/CaseList.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('title="OPEN CASES"', 'label="OPEN CASES"')
content = content.replace('title="AT RISK"', 'label="AT RISK"')
content = content.replace('title="AWAITING APPROVAL"', 'label="AWAITING APPROVAL"')
content = content.replace('title="IN EXECUTION"', 'label="IN EXECUTION"')
content = content.replace('titleColor=', 'labelColor=')

with open('frontend/src/pages/CaseList.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
