with open('frontend/src/pages/Dashboard.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("to={`/cases/${pd.id}`}", "to={`/cases/${pd?.id}`}")
content = content.replace("currentState={pd.workflow_state}", "currentState={pd?.workflow_state || 'UNKNOWN'}")

with open('frontend/src/pages/Dashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed final TS errors")
