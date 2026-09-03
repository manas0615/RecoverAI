import pytest
from fastapi.testclient import TestClient
from datetime import UTC, datetime, timedelta
import time
import asyncio

from recoverai.api.main import app, rate_limiter
from recoverai.config import settings

@pytest.fixture
def client():
    rate_limiter.history.clear()
    return TestClient(app)

def test_rate_limit_below_limit(client, monkeypatch):
    rate_limiter.history.clear()
    monkeypatch.setattr(settings, 'rate_limit_calls', 5)

    for _ in range(4):
        response = client.post(
            '/mcp/execute', 
            headers={'Authorization': f'Bearer {settings.n8n_api_key}'},
            json={'tool': 'fake', 'args': {}}
        )
        assert response.status_code != 429

def test_rate_limit_exceeded(client, monkeypatch):
    rate_limiter.history.clear()
    monkeypatch.setattr(settings, 'rate_limit_calls', 2)

    for _ in range(2):
        response = client.post(
            '/mcp/execute', 
            headers={'Authorization': f'Bearer {settings.n8n_api_key}'},
            json={'tool': 'fake', 'args': {}}
        )
        assert response.status_code != 429

    response = client.post(
        '/mcp/execute', 
        headers={'Authorization': f'Bearer {settings.n8n_api_key}'},
        json={'tool': 'fake', 'args': {}}
    )
    assert response.status_code == 429

def test_rate_limit_independent_buckets(monkeypatch):
    from recoverai.api.main import RateLimiter
    from fastapi import HTTPException

    monkeypatch.setattr(settings, 'rate_limit_calls', 1)

    limiter = RateLimiter(period=60)

    class MockClient:
        def __init__(self, host):
            self.host = host

    class MockRequest:
        def __init__(self, host):
            self.client = MockClient(host)

    req1 = MockRequest('1.1.1.1')
    req2 = MockRequest('2.2.2.2')

    limiter(req1)
    limiter(req2)

    with pytest.raises(HTTPException) as exc:
        limiter(req1)
    assert exc.value.status_code == 429

    with pytest.raises(HTTPException) as exc:
        limiter(req2)
    assert exc.value.status_code == 429

def test_rate_limit_window_reset(monkeypatch):
    from recoverai.api.main import RateLimiter
    from fastapi import HTTPException

    monkeypatch.setattr(settings, 'rate_limit_calls', 1)

    limiter = RateLimiter(period=1)

    class MockClient:
        host = '1.1.1.1'
    class MockRequest:
        client = MockClient()

    req = MockRequest()

    limiter(req)

    with pytest.raises(HTTPException) as exc:
        limiter(req)
    assert exc.value.status_code == 429

    limiter.history['1.1.1.1'][0] = limiter.history['1.1.1.1'][0] - timedelta(seconds=2)

    limiter(req)

def test_webhook_not_throttled(client, monkeypatch):
    rate_limiter.history.clear()
    monkeypatch.setattr(settings, 'rate_limit_calls', 1)

    for _ in range(5):
        response = client.post(
            '/webhooks/razorpay/merch_123',
            headers={'X-Razorpay-Signature': 'fake', 'X-Razorpay-Event-Id': 'evt_123'},
            json={}
        )
        assert response.status_code != 429
