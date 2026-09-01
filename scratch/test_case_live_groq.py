from fastapi.testclient import TestClient
from recoverai.api.main import app
import json
from recoverai.config import settings

client = TestClient(app)

print("=== case_LIVE (Groq Test) ===")
resp_live = client.post('/recovery-cases/case_LIVE/analyze', headers={"X-API-Key": settings.frontend_api_key})
print(json.dumps(resp_live.json(), indent=2))
