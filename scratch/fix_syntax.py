import re

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('className="relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] shrink-0 mr-4 transition-colors duration-300 " + circleClass}>', 'className={"relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] shrink-0 mr-4 transition-colors duration-300 " + circleClass}>')

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
