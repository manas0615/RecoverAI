import re

with open('frontend/src/pages/AnalyticsPage.tsx', 'r') as f:
    content = f.read()

content = content.replace('<MoneyValue amount={verified_recovered.INR || 0} currency="INR" />', '<MoneyValue value={verified_recovered.INR || 0} currency="INR" />')
content = content.replace('<MoneyValue amount={revenue_at_risk.INR || 0} currency="INR" />', '<MoneyValue value={revenue_at_risk.INR || 0} currency="INR" />')
content = content.replace('formatter={(value: number) => formatCurrency(value)}', 'formatter={(value: any) => formatCurrency(Number(value))}')
content = content.replace("labelFormatter={(label) => new Date(label).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}", "labelFormatter={(label: any) => new Date(label as string).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}")

with open('frontend/src/pages/AnalyticsPage.tsx', 'w') as f:
    f.write(content)
