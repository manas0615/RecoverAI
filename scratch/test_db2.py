import pytest
from recoverai.persistence.connection import TransactionManager
from recoverai.config import settings

def test_db():
    tm = TransactionManager(settings.database_url)
    with tm.transaction() as conn:
        print(conn.execute("PRAGMA foreign_keys").fetchall())
        print(conn.execute("SELECT * FROM merchants").fetchall())
