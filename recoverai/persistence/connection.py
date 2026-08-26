import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from recoverai.config import settings


def _dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class TransactionManager:
    """
    Manages SQLite connections and provides transaction boundaries.
    """

    def __init__(self, db_url: str | None = None):
        self.db_url = db_url or settings.database_url
        self._parsed_path = self._parse_url(self.db_url)

    def _parse_url(self, url: str) -> str:
        if url.startswith("sqlite:///"):
            return url[10:]
        elif url.startswith("sqlite://"):
            return url[9:]
        return url

    def create_connection(self) -> sqlite3.Connection:
        # uri=True allows 'file::memory:?cache=shared' etc.
        # check_same_thread=False allows us to share a memory DB across testing threads if needed
        # though normally we only pass the connection around.
        conn = sqlite3.connect(self._parsed_path, uri=True, check_same_thread=False)
        conn.row_factory = _dict_factory
        # Enforce foreign keys (requires SQLite >= 3.6.19)
        conn.execute("PRAGMA foreign_keys = ON;")
        # Set journal mode for better concurrency
        if self._parsed_path != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Yields an active SQLite connection and commits on success,
        or rolls back if an exception occurs.
        """
        conn = self.create_connection()
        try:
            # Begin explicit transaction (SQLite defers locks until needed,
            # but 'BEGIN' starts a logical boundary)
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def run_migrations(self, migrations_dir: str | Path | None = None) -> None:
        """
        Runs sequentially ordered .sql files.
        """
        if not migrations_dir:
            base_dir = Path(__file__).parent
            migrations_dir = base_dir / "migrations"
        else:
            migrations_dir = Path(migrations_dir)

        with self.transaction() as conn:
            # Create migrations table if not exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
            """)

            # Find all migration files
            migration_files = sorted(migrations_dir.glob("*.sql"))
            for mf in migration_files:
                try:
                    version = int(mf.stem.split("_")[0])
                except ValueError:
                    continue

                # Check if applied
                cur = conn.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
                )
                if cur.fetchone():
                    continue

                # Run migration
                with open(mf, "r", encoding="utf-8") as f:
                    script = f.read()

                conn.executescript(script)

                # Record
                conn.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                    (version, datetime.now(UTC).isoformat()),
                )
