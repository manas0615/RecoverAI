import os
import tempfile
import urllib.request
from unittest.mock import MagicMock
import json

import pytest

test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

# Ensure tables are created
from recoverai.persistence.connection import TransactionManager

tm = TransactionManager(f"sqlite:///{test_db_path}")
tm.run_migrations()


@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("RAZORPAY_MODE", "test")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{test_db_path}")

    # Explicitly clear real credentials to prevent accidental loading
    monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
    monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)
    
    # Disable high_value_threshold by default for backward compatibility with existing tests
    monkeypatch.setattr("recoverai.config.settings.high_value_threshold_inr", None)
    
    # Disable rate limits globally for the test suite
    monkeypatch.setattr("recoverai.config.settings.rate_limit_calls", 10000)

@pytest.fixture
def fake_razorpay(monkeypatch: pytest.MonkeyPatch):
    from recoverai.integrations.razorpay.adapter import RazorpayExecutionResult, RazorpayExecutionResultType
    
    mock_execute = MagicMock(return_value=RazorpayExecutionResult(
        result_type=RazorpayExecutionResultType.SUCCESSFUL_REQUEST,
        provider_reference="plink_mocked_explicitly",
        short_url="https://rzp.io/i/mocked"
    ))
    
    from recoverai.api.main import container
    monkeypatch.setattr(container.rzp_adapter, "execute_payment_link", mock_execute)
    return mock_execute

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    try:
        os.close(test_db_fd)
        os.remove(test_db_path)
    except Exception:
        pass
