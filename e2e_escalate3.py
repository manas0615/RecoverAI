import requests, json, os
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_KEY = os.getenv("FRONTEND_API_KEY", "dev_frontend_key")
N8N_KEY = os.getenv("N8N_API_KEY", "dev_n8n_key")

resp = requests.get(f"{BASE_URL}/recovery-cases/", headers={"X-API-Key": FRONTEND_KEY})
case_id = next(c["case_id"] for c in resp.json()["cases"] if c["amount_minor"] == 500000000 and c["status"] == "OPEN")

time_resp = requests.get(f"{BASE_URL}/recovery-cases/{case_id}/timeline", headers={"X-API-Key": FRONTEND_KEY})
events = time_resp.json()["events"]
act_id = next(e["action_id"] for e in reversed(events) if e["action_id"] is not None)

print(f"Action ID to approve: {act_id}")
appr_resp = requests.post(f"{BASE_URL}/recovery-cases/{case_id}/actions/{act_id}/approve", headers={"X-API-Key": FRONTEND_KEY})
print("Approve Response:", appr_resp.text)

# Execute now
exec_resp = requests.post(f"{BASE_URL}/mcp/execute", headers={"X-API-Key": N8N_KEY}, json={"tool": "create_payment_link", "args": {"case_id": case_id, "action_id": act_id}})
print("Execute Response:", exec_resp.text)
