import re

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "actorType: string | undefined, eventType: string, actorId: string | undefined",
    "actorType: string | undefined | null, eventType: string, actorId: string | undefined | null"
)

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
