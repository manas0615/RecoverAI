with open("recoverai/application/action_service.py", "r", encoding="utf-8") as f:
    for line in f:
        if "execute" in line:
            print(line, end="")
