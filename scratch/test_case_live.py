from fastapi.testclient import TestClient
from recoverai.api.main import app
import json
import os
from recoverai.config import settings

client = TestClient(app)
resp = client.post('/recovery-cases/case_LIVE/analyze', headers={"X-Frontend-API-Key": settings.frontend_api_key})
print(json.dumps(resp.json(), indent=2))
