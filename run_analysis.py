import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_KEY = "test_frontend_key_default"
CASE_ID = "case_TXDBvr4RrbgdC8"

print(f"Analyzing case {CASE_ID}...")
resp = requests.post(f"{BASE_URL}/recovery-cases/{CASE_ID}/analyze", headers={"X-API-Key": API_KEY})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print("Analyze OK!")
else:
    print(resp.text)
    
time.sleep(2)

case_detail = requests.get(f"{BASE_URL}/recovery-cases/{CASE_ID}", headers={"X-API-Key": API_KEY}).json()
print("Case Status:", case_detail.get("status"))
print("Policy Decision:", case_detail.get("policy_decision"))
print("Action Status:", case_detail.get("action_status"))
print("Execution Ref (Payment Link):", case_detail.get("workflow_execution_reference"))
