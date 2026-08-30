import os
import tempfile

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
    """
    Ensure all tests run with test environment values.
    This prevents accidental loading of real environment variables during tests.
    """
    monkeypatch.setenv("RAZORPAY_MODE", "test")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{test_db_path}")


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    try:
        os.close(test_db_fd)
        os.remove(test_db_path)
    except Exception:  # noqa: BLE001, S110
        pass
