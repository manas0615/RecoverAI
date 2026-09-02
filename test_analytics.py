from fastapi.testclient import TestClient
from recoverai.api.main import app
from recoverai.config import settings
import json

client = TestClient(app)
resp = client.get("/analytics", headers={"X-API-Key": settings.frontend_api_key})
print(json.dumps(resp.json().get("verification_outcomes", {}), indent=2))
