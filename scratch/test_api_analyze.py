import httpx
import logging
logging.basicConfig(level=logging.DEBUG)

from fastapi.testclient import TestClient
from recoverai.api.main import app
from recoverai.config import get_settings

settings = get_settings()
client = TestClient(app)

headers = {"x-api-key": settings.frontend_api_key}
res = client.post("/recovery-cases/case_LIVE/analyze", headers=headers)
print(res.status_code)
print(res.json())

