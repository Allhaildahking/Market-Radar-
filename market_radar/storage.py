import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class Store:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS seen (
                item_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                published TEXT,
                detected TEXT NOT NULL,
                alert_level TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS source_state (
                source TEXT PRIMARY KEY,
                etag TEXT,
                modified TEXT,
                last_checked TEXT,
                last_success TEXT,
                last_error TEXT
            )
        """)
        self.db.commit()

    def has_seen(self, item_id: str) -> bool:
        row = self.db.execute("SELECT 1 FROM seen WHERE item_id=?", (item_id,)).fetchone()
        return row is not None

    def save_item(self, item: dict) -> None:
        self.db.execute(
            "INSERT OR IGNORE INTO seen VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item["id"], item["source"], item["title"], item["link"],
             item.get("published"), item["detected"], item["level"])
        )
        self.db.commit()

    def source_headers(self, source: str) -> dict:
        row = self.db.execute(
            "SELECT etag, modified FROM source_state WHERE source=?", (source,)
        ).fetchone()
        if not row:
            return {}
        headers = {}
        if row[0]:
            headers["If-None-Match"] = row[0]
        if row[1]:
            headers["If-Modified-Since"] = row[1]
        return headers

    def update_source(self, source: str, etag=None, modified=None, error=None, success=False):
        now = datetime.now(timezone.utc).isoformat()
        self.db.execute("""
            INSERT INTO source_state(source, etag, modified, last_checked, last_success, last_error)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source) DO UPDATE SET
              etag=COALESCE(excluded.etag, source_state.etag),
              modified=COALESCE(excluded.modified, source_state.modified),
              last_checked=excluded.last_checked,
              last_success=CASE WHEN ? THEN excluded.last_success ELSE source_state.last_success END,
              last_error=excluded.last_error
        """, (source, etag, modified, now, now if success else None, error, int(success)))
        self.db.commit()

    def close(self):
        self.db.close()
