import re
with open('recoverai/api/main.py', 'r') as f:
    text = f.read()
text = text.replace('risk.model_version if risk else "UNKNOWN"', 'plan.selection_model_version if plan else "UNKNOWN"')
with open('recoverai/api/main.py', 'w') as f:
    f.write(text)
