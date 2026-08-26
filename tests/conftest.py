import pytest


@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch: pytest.MonkeyPatch):
    """
    Ensure all tests run with test environment values.
    This prevents accidental loading of real environment variables during tests.
    """
    monkeypatch.setenv("RAZORPAY_MODE", "test")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
