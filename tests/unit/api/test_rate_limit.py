import pytest
from fastapi.testclient import TestClient
from datetime import UTC, datetime, timedelta
import time

from recoverai.api.main import app, rate_limiter
from recoverai.config import settings

@pytest.fixture
def client():
    # Reset state
    rate_limiter.history.clear()
    rate_limiter.calls = 5
    rate_limiter.period = timedelta(seconds=60)
    return TestClient(app)

def test_rate_limit_below_limit(client):
    rate_limiter.history.clear()
    rate_limiter.calls = 5
    
    # We mock out execute_mcp_tool dependency/registry logic by just checking status code is not 429
    # Send 4 requests
    for _ in range(4):
        response = client.post(
            "/mcp/execute", 
            headers={"Authorization": f"Bearer {settings.n8n_api_key}"},
            json={"tool": "fake", "args": {}}
        )
        assert response.status_code != 429
        
def test_rate_limit_exceeded(client):
    rate_limiter.history.clear()
    rate_limiter.calls = 2
    
    for _ in range(2):
        response = client.post(
            "/mcp/execute", 
            headers={"Authorization": f"Bearer {settings.n8n_api_key}"},
            json={"tool": "fake", "args": {}}
        )
        assert response.status_code != 429
        
    # Third should fail with 429
    response = client.post(
        "/mcp/execute", 
        headers={"Authorization": f"Bearer {settings.n8n_api_key}"},
        json={"tool": "fake", "args": {}}
    )
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    
def test_rate_limit_independent_buckets(client, monkeypatch):
    rate_limiter.history.clear()
    rate_limiter.calls = 2
    
    # 2 calls from IP A
    from fastapi import Request
    original_client = Request.client
    
    # Mocking client IP is easier by overriding the history directly, or we can just assume the tests prove the code uses client_ip as bucket key.
    # The rate limiter code: client_ip = request.client.host if request.client else "127.0.0.1"
    # To test buckets, let's just test the RateLimiter directly
    from recoverai.api.main import RateLimiter
    import pytest
    from fastapi import HTTPException
    
    limiter = RateLimiter(calls=1, period=60)
    
    class MockClient:
        def __init__(self, host):
            self.host = host
            
    class MockRequest:
        def __init__(self, host):
            self.client = MockClient(host)
            
    req1 = MockRequest("1.1.1.1")
    req2 = MockRequest("2.2.2.2")
    
    # IP 1 call 1 (OK)
    limiter(req1)
    
    # IP 2 call 1 (OK)
    limiter(req2)
    
    # IP 1 call 2 (429)
    with pytest.raises(HTTPException) as exc:
        limiter(req1)
    assert exc.value.status_code == 429
    
    # IP 2 call 2 (429)
    with pytest.raises(HTTPException) as exc:
        limiter(req2)
    assert exc.value.status_code == 429

def test_rate_limit_window_reset():
    from recoverai.api.main import RateLimiter
    from fastapi import HTTPException
    import pytest
    
    limiter = RateLimiter(calls=1, period=1) # 1 sec window
    
    class MockClient:
        host = "1.1.1.1"
    class MockRequest:
        client = MockClient()
        
    req = MockRequest()
    
    # Call 1 OK
    limiter(req)
    
    # Call 2 fails
    with pytest.raises(HTTPException) as exc:
        limiter(req)
    assert exc.value.status_code == 429
    
    # We must patch datetime to simulate time passing, or we can just monkeypatch the history timestamp directly
    limiter.history["1.1.1.1"][0] = limiter.history["1.1.1.1"][0] - timedelta(seconds=2)
    
    # Call 3 OK
    limiter(req)

def test_webhook_not_throttled(client):
    rate_limiter.history.clear()
    rate_limiter.calls = 1
    
    # Mocking webhook payload doesn't need to be perfectly valid to bypass rate limiting (it'll fail with 400 signature, not 429)
    for _ in range(5):
        response = client.post(
            "/webhooks/razorpay/merch_123",
            headers={"X-Razorpay-Signature": "fake", "X-Razorpay-Event-Id": "evt_123"},
            json={}
        )
        assert response.status_code != 429 # should be 400 or something, but not 429
