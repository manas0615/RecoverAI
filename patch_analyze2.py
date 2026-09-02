import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("setattr(action, \"_real_cause\", cause)", "setattr(action, \"_real_cause\", cause)\n            import json\n            if plan:\n                action.plan_snapshot = json.dumps(plan.model_dump())")

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py")
