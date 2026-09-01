import re
with open('frontend/src/pages/CaseDetailView.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to change the condition for "Analysis not yet run".
old_condition = ": (caseData.recommendation === 'N/A' || !caseData.recommendation) && !caseData.policy_decision ?"
new_condition = ": (caseData.recommendation === 'N/A' || !caseData.recommendation) && !caseData.policy_decision && !timeline.some(e => ['LLM_RECOMMENDATION_CREATED', 'POLICY_DECISION_CREATED', 'ANALYSIS_STARTED'].includes(e.event_type)) ?"

content = content.replace(old_condition, new_condition)

with open('frontend/src/pages/CaseDetailView.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
