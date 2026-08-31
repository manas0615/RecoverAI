import os

with open('frontend/src/pages/Dashboard.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("function KpiCard({ title, value, titleColor = 'text-[var(--color-text-secondary)]', valueColor = 'text-[var(--color-text-primary)]', icon = null }) {", "function KpiCard({ title, value, titleColor = 'text-[var(--color-text-secondary)]', valueColor = 'text-[var(--color-text-primary)]', icon = null }: { title: string, value: React.ReactNode, titleColor?: string, valueColor?: string, icon?: React.ReactNode }) {")

content = content.replace("import { AlertTriangle, FileText, Activity, Server, Zap, CheckCircle2, Circle, AlertCircle, RefreshCw } from 'lucide-react';", "import { AlertTriangle, FileText, Zap, CheckCircle2 } from 'lucide-react';")

content = content.replace("const { data: healthData } = useHealth();", "")
content = content.replace("const { data, loading } = useCases();", "const { data } = useCases();")

content = content.replace("value={metrics ? <MoneyValue amountMinor={metrics.revenueRecovered} currency=\"INR\" /> : '...'}", "value={metrics ? <MoneyValue amountMinor={metrics.revenueRecovered} currency=\"INR\" /> : null}")
content = content.replace("value={metrics ? <MoneyValue amountMinor={metrics.revenueAtRisk} currency=\"INR\" /> : '...'}", "value={metrics ? <MoneyValue amountMinor={metrics.revenueAtRisk} currency=\"INR\" /> : null}")

with open('frontend/src/pages/Dashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

with open('frontend/src/components/layout/AppShell.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("import { TestModeBadge } from '../status/TestModeBadge';", "")

with open('frontend/src/components/layout/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed TS")
