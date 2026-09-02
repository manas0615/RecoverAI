with open("recoverai/integrations/razorpay/adapter.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
in_func = False
for line in lines:
    if "def execute_payment_link" in line:
        in_func = True
    if in_func:
        print(line, end="")
        if "except TimeoutError:" in line:
            break
