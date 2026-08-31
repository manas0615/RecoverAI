with open('frontend/src/types/domain.ts', 'r', encoding='utf-8') as f:
    content = f.read()

new_fields = "    workflow_state?: string;\n    failure_code?: string;\n    recommendation?: string;\n    updated_at?: string;"
content = content.replace("    workflow_state?: string;", new_fields)

with open('frontend/src/types/domain.ts', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated domain.ts")
