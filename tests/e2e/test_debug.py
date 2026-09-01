import pytest
import os
import hmac
import hashlib
import json
import uuid
from datetime import datetime, UTC
from fastapi.testclient import TestClient

from recoverai.api.main import app
from recoverai.config import settings

client = TestClient(app)

def test_debug(client):
    resp = client.get("/recovery-cases/", headers={"X-API-Key": settings.frontend_api_key})
    cases = resp.json()["cases"]
    c = cases[0]
    print(c["case_id"], c["action_status"], c["status"])

