import re

with open('recoverai/api/main.py', 'r') as f:
    text = f.read()

# Replace the specific line:
# "confidence": cause.confidence.value if cause else None,

replacement = '''"confidence": (
                            next((c.expected_recovery_probability.value for c in plan.candidates if c.action_type == plan.selected_action_type), None)
                            if plan else None
                        ),'''

text = text.replace('"confidence": cause.confidence.value if cause else None,', replacement)

with open('recoverai/api/main.py', 'w') as f:
    f.write(text)

