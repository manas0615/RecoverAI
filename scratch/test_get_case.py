import pytest
from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings
from recoverai.persistence.connection import TransactionManager

client = TestClient(app)
resp = client.get("/recovery-cases/", headers={"X-API-Key": settings.frontend_api_key})
cases = resp.json()["cases"]
if cases:
    print(client.get(f"/recovery-cases/{cases[0]['case_id']}", headers={"X-API-Key": settings.frontend_api_key}).json())
