import re

with open('frontend/src/pages/AnalyticsPage.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<p className="text-xs text-[var(--color-text-muted)]">Comparison against standard deterministic rule-based recovery.</p>',
    '<p className="text-xs text-[var(--color-text-muted)]">Recovery Rate (Case) comparison against standard deterministic rule-based recovery.</p>'
)

with open('frontend/src/pages/AnalyticsPage.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
