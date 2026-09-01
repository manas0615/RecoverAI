import re
with open('recoverai/api/main.py', 'r') as f:
    text = f.read()
text = text.replace('id=risk.model_name', 'id=plan.selection_model_version if plan else "UNKNOWN"')
with open('recoverai/api/main.py', 'w') as f:
    f.write(text)
