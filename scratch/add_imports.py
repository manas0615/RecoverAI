with open('frontend/src/pages/Dashboard.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

imports_to_add = "import { Link } from 'react-router-dom';\nimport { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid } from 'recharts';\n"

if "import { Link } from 'react-router-dom';" not in content:
    content = imports_to_add + content

# Also fix the any types in tickFormatter
content = content.replace("tickFormatter={(val) =>", "tickFormatter={(val: any) =>")
content = content.replace("formatter={(val, name) =>", "formatter={(val: any, name: any) =>")
content = content.replace("labelFormatter={(label) =>", "labelFormatter={(label: any) =>")

with open('frontend/src/pages/Dashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added imports")
