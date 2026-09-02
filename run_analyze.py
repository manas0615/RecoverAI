from fastapi.testclient import TestClient
from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)
resp = client.post(
    f"/recovery-cases/case_TXDBvr4RrbgdC8/analyze",
    headers={"X-API-Key": settings.frontend_api_key},
)
print(resp.status_code)
print(resp.text)
