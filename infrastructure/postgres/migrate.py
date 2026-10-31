"""
infrastructure/postgres/migrate.py
-----------------------------------
Lightweight migration runner for Educentriks Cognify.

Usage (from the repo root, with the venv active):
    python infrastructure/postgres/migrate.py

It will:
  1. Connect to PostgreSQL using infrastructure/postgres/.env
  2. Create a schema_migrations tracking table if absent
  3. Run any SQL files in migrations/ that have not been applied yet
  4. Record each applied migration with a timestamp
"""

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
ENV_FILE = Path(__file__).parent / ".env"

load_dotenv(ENV_FILE)


def get_connection() -> psycopg.Connection:
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        sys.exit("ERROR: POSTGRES_PASSWORD is not set in infrastructure/postgres/.env")

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "agentic_db"),
        user=os.getenv("POSTGRES_USER", "agentic"),
        password=password,
        autocommit=False,
    )


# ── Migration tracking table ──────────────────────────────────────────────────

CREATE_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename    TEXT        PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def ensure_tracking_table(conn: psycopg.Connection) -> None:
    conn.execute(CREATE_TRACKING_TABLE)
    conn.commit()


def applied_migrations(conn: psycopg.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT filename FROM schema_migrations ORDER BY filename"
    ).fetchall()
    return {row[0] for row in rows}


def record_migration(conn: psycopg.Connection, filename: str) -> None:
    conn.execute(
        "INSERT INTO schema_migrations (filename) VALUES (%s)", (filename,)
    )


# ── Runner ────────────────────────────────────────────────────────────────────

def run_migrations() -> None:
    if not MIGRATIONS_DIR.exists():
        sys.exit(f"ERROR: migrations directory not found at {MIGRATIONS_DIR}")

    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        print("No migration files found — nothing to do.")
        return

    conn = get_connection()
    try:
        ensure_tracking_table(conn)
        already_applied = applied_migrations(conn)

        pending = [f for f in sql_files if f.name not in already_applied]
        if not pending:
            print("All migrations are already applied — database is up to date.")
            return

        for sql_file in pending:
            print(f"  Applying {sql_file.name} … ", end="", flush=True)
            sql = sql_file.read_text(encoding="utf-8")
            conn.execute(sql)
            record_migration(conn, sql_file.name)
            conn.commit()
            print("done")

        print(f"\n✓ Applied {len(pending)} migration(s) successfully.")

    except Exception as exc:
        conn.rollback()
        print(f"\nERROR: migration failed — {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()

