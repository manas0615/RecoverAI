with open("recoverai/api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_get_case = """        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        if case.status.value == "CLOSED":
            raise HTTPException(status_code=400, detail="INVALID_STATE: Case is closed")"""

good_get_case = """        if not case:
            raise HTTPException(status_code=404, detail="Case not found")"""

# We only want to replace the first occurrence (get_case)
content = content.replace(bad_get_case, good_get_case, 1)

with open("recoverai/api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Removed closed check from get_case.")
