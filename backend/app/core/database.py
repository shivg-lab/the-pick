import json
import sqlite3
from pathlib import Path
from app.models.domain import Feedback, RecommendationResponse

MIGRATIONS = [
    (
        1,
        """
CREATE TABLE recommendations (request_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL);
CREATE TABLE feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT NOT NULL REFERENCES recommendations(request_id),
 event_id TEXT NOT NULL, rating TEXT, would_attend INTEGER, reason TEXT NOT NULL, correction TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX feedback_request_idx ON feedback(request_id);
""",
    )
]


class Repository:
    """SQL is isolated here for a future PostgreSQL/SQLAlchemy repository adapter."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            for n, sql in MIGRATIONS:
                if n > version:
                    conn.executescript(sql)
                    conn.execute(f"PRAGMA user_version={n}")

    def connect(self):
        conn = sqlite3.connect(self.path, timeout=5)
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def save(self, response: RecommendationResponse):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO recommendations VALUES (?,?,?)",
                (response.request_id, response.created_at.isoformat(), response.model_dump_json()),
            )

    def get(self, id: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM recommendations WHERE request_id=?", (id,)).fetchone()
        return json.loads(row[0]) if row else None

    def feedback(self, data: Feedback) -> int:
        result = self.get(data.request_id)
        if not result or data.event_id not in {r["event"]["id"] for r in result["recommendations"]}:
            raise ValueError("Select an event from a stored recommendation")
        with self.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO feedback (request_id,event_id,rating,would_attend,reason,correction) VALUES (?,?,?,?,?,?)",
                (data.request_id, data.event_id, data.rating, data.would_attend, data.reason, data.correction),
            )
            return cursor.lastrowid
