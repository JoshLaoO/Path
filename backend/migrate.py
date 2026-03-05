"""
One-time schema migration for existing SQLite databases.
Adds columns that were added to models after the initial create_all.
Run at app startup after Base.metadata.create_all().
"""
from sqlalchemy import text

from database import engine


def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(text(f"PRAGMA table_info({table})"))
    return any(row[1] == column for row in result.fetchall())


def _table_exists(conn, table: str) -> bool:
    result = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table},
    )
    return result.fetchone() is not None


def run_migrations() -> None:
    """Add any missing columns to existing tables (SQLite)."""
    if not str(engine.url).startswith("sqlite"):
        return
    with engine.connect() as conn:
        if _table_exists(conn, "plans") and not _column_exists(conn, "plans", "user_id"):
            conn.execute(
                text(
                    "ALTER TABLE plans ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1"
                )
            )
            conn.commit()

        if _table_exists(conn, "plan_days") and not _column_exists(
            conn, "plan_days", "verse"
        ):
            conn.execute(text("ALTER TABLE plan_days ADD COLUMN verse TEXT"))
            conn.commit()

        if _table_exists(conn, "plan_days") and not _column_exists(
            conn, "plan_days", "passage_reference"
        ):
            conn.execute(
                text("ALTER TABLE plan_days ADD COLUMN passage_reference TEXT")
            )
            conn.commit()

        if _table_exists(conn, "plan_days") and not _column_exists(
            conn, "plan_days", "key_verse"
        ):
            conn.execute(text("ALTER TABLE plan_days ADD COLUMN key_verse TEXT"))
            conn.commit()

        # Ensure user 1 exists so plans.user_id=1 is valid
        if _table_exists(conn, "users"):
            result = conn.execute(text("SELECT 1 FROM users WHERE id = 1"))
            if result.fetchone() is None:
                conn.execute(
                    text(
                        "INSERT INTO users (id, email, hashed_password) VALUES (1, :email, :pw)"
                    ),
                    {"email": "default@example.com", "pw": "placeholder"},
                )
                conn.commit()
