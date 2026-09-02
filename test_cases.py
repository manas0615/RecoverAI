from fastapi.testclient import TestClient
from recoverai.api.main import app
from recoverai.config import settings
import json

client = TestClient(app)
resp = client.get("/recovery-cases/", headers={"X-API-Key": settings.frontend_api_key})
cases = [c for c in resp.json()["cases"] if c["action_status"] == "VERIFICATION_PENDING"]
for c in cases:
    print(c["case_id"], c["action_status"], c.get("verification_state"))
