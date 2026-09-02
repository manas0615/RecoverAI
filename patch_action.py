with open("recoverai/application/action_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "if result.result_type == RazorpayExecutionResultType.SUCCESSFUL_REQUEST:" in line:
        lines[i] = "            if result.result_type in (RazorpayExecutionResultType.SUCCESSFUL_REQUEST, RazorpayExecutionResultType.PROVIDER_REJECTED):\n"

with open("recoverai/application/action_service.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Patched action_service.py")
