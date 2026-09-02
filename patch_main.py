import re

with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'd["external_reference"] = getattr(\n                        latest_action, "external_reference", None\n                    )',
    'd["external_reference"] = getattr(latest_action, "external_reference", None)\n                    d["workflow_execution_reference"] = getattr(latest_action, "workflow_execution_reference", None)'
)

content = content.replace(
    'd["external_reference"] = None',
    'd["external_reference"] = None\n                    d["workflow_execution_reference"] = None'
)

content = content.replace(
    'result["external_reference"] = getattr(\n                    latest_action, "external_reference", None\n                )',
    'result["external_reference"] = getattr(latest_action, "external_reference", None)\n                result["workflow_execution_reference"] = getattr(latest_action, "workflow_execution_reference", None)'
)

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py")
