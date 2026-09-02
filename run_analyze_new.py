from fastapi.testclient import TestClient
from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)
resp = client.post(
    f"/recovery-cases/case_ev_2384c26f96a5/analyze",
    headers={"X-API-Key": settings.frontend_api_key},
)
print(resp.status_code)
print(resp.text)
