with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("action.plan_snapshot = json.dumps(plan.model_dump())", "action.plan_snapshot = json.dumps(plan.to_dict())")

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed main.py")
