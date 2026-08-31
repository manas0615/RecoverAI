import re

with open('frontend/src/pages/AnalyticsPage.tsx', 'r') as f:
    content = f.read()

content = content.replace('<MoneyValue value={verified_recovered.INR || 0} currency="INR" />', '<MoneyValue amountMinor={verified_recovered.INR || 0} currency="INR" />')
content = content.replace('<MoneyValue value={revenue_at_risk.INR || 0} currency="INR" />', '<MoneyValue amountMinor={revenue_at_risk.INR || 0} currency="INR" />')

with open('frontend/src/pages/AnalyticsPage.tsx', 'w') as f:
    f.write(content)
