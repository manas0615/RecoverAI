import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)
resp = client.get("/recovery-cases/case_LIVE", headers={"X-API-Key": settings.frontend_api_key})
print(resp.json())
