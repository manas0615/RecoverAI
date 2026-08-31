with open('frontend/src/types/domain.ts', 'r', encoding='utf-8') as f:
    content = f.read()

new_fields = """  updated_at?: string;
  failure_code?: string;
  historical_failure_count?: number;
  recommendation?: string;
  confidence?: number;
  reasoning?: string;
  provenance?: string;
  policy_decision?: string;
  policy_reasons?: string[];
  action_id?: string;"""

if 'historical_failure_count' not in content:
    content = content.replace("updated_at?: string;", new_fields)
    with open('frontend/src/types/domain.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated domain.ts")
