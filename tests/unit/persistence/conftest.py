import os
import tempfile

import pytest

from recoverai.persistence.connection import TransactionManager


@pytest.fixture
def tm():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    manager = TransactionManager(f"sqlite:///{path}")
    manager.run_migrations()

    with manager.transaction() as conn:
        conn.execute("""
            INSERT INTO merchants (merchant_id, display_name, default_currency, status, created_at, updated_at)
            VALUES ('m_1', 'Test Merchant', 'INR', 'ACTIVE', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00')
        """)
        conn.execute("""
            INSERT INTO customers (customer_id, merchant_id, created_at, updated_at)
            VALUES ('c_1', 'm_1', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00')
        """)

    yield manager

    # Cleanup
    try:
        os.remove(path)
    except OSError:
        pass
