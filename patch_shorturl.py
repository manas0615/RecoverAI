import re

with open("recoverai/integrations/razorpay/service.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("action.external_reference = result.provider_reference", "action.external_reference = result.provider_reference\n        if result.short_url:\n            action.workflow_execution_reference = result.short_url")

with open("recoverai/integrations/razorpay/service.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated service.py")
