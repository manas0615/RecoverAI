import re

with open('frontend/src/pages/CaseDetailView.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<RecoveryJourney caseData={caseData} />', '<RecoveryJourney currentState={caseData.workflow_state || \'\'} />')
content = content.replace('event.occurred_at || event.timestamp', 'event.timestamp')

with open('frontend/src/pages/CaseDetailView.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
