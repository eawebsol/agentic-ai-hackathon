from api.database import get_connection


CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS learners (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    "current_role" TEXT,
    experience_level VARCHAR(50) NOT NULL DEFAULT 'beginner',
    target_certification VARCHAR(50) NOT NULL DEFAULT 'AI-103',
    learning_preferences JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);
"""


def init_db():
    with get_connection() as conn:
        conn.execute(CREATE_TABLE)

    print("Database initialized: learners table is ready.")


if __name__ == "__main__":
    init_db()
