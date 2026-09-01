import re
with open('frontend/src/components/financial/RecoveryJourney.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("if (eventType === 'LLM_RECOMMENDATION_CREATED') return 'Gemini';", "if (eventType === 'LLM_RECOMMENDATION_CREATED') return actorId.includes('deterministic') ? 'Deterministic Fallback' : actorId;")

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
