import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)
resp = client.post("/recovery-cases/case_LIVE/analyze", headers={"X-API-Key": settings.frontend_api_key})
print(resp.json())
