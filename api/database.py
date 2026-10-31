import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / "infrastructure" / "postgres" / ".env")


def get_connection():
    password = os.environ.get("POSTGRES_PASSWORD")

    if not password:
        raise RuntimeError("POSTGRES_PASSWORD is not configured")

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "agentic_db"),
        user=os.getenv("POSTGRES_USER", "agentic"),
        password=password,
        row_factory=dict_row,
    )
