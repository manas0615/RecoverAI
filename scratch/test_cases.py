from fastapi.testclient import TestClient
from recoverai.api.main import app
import json
import os
from recoverai.config import settings

client = TestClient(app)

print("=== case_LIVE ===")
resp_live = client.post('/recovery-cases/case_LIVE/analyze', headers={"X-API-Key": settings.frontend_api_key})
print(json.dumps(resp_live.json(), indent=2))

print("\n=== case_DUPLICATE ===")
resp_dup = client.post('/recovery-cases/case_DUPLICATE/analyze', headers={"X-API-Key": settings.frontend_api_key})
print(json.dumps(resp_dup.json(), indent=2))
