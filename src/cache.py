"""SQLite cache for bookmark status tracking."""

import sqlite3
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, Any
from pathlib import Path

from .config import settings

logger = logging.getLogger(__name__)

def retry_on_locked(func: Any) -> Any:
    """Retry function on database locked error."""
    def wrapper(*args, **kwargs):
        max_retries = 5
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and i < max_retries - 1:
                    logger.warning("Database locked, retrying... (%d/%d)", i + 1, max_retries)
                    continue
                raise
    return wrapper


class Cache:
    """SQLite cache for bookmark status tracking."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.cache_db_path
        self._conn = None
        self._init_db()
    
    def _ensure_db_dir(self):
        """Ensure database directory exists."""
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_db(self):
        """Initialize database schema."""
        self._ensure_db_dir()
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(self.db_path)
            self._create_schema(self._conn)
    
    def _get_connection(self):
        """Get database connection."""
        if self.db_path == ":memory:":
            return self._conn
        conn = sqlite3.connect(self.db_path)
        self._create_schema(conn)
        return conn
    
    def _create_schema(self, conn):
        """Create database schema."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id TEXT PRIMARY KEY,
                last_status TEXT NOT NULL,
                consecutive_failures INTEGER NOT NULL DEFAULT 0,
                last_final_url TEXT,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    @retry_on_locked
    def get_status(self, bookmark_id: str) -> Optional[Tuple[str, int, Optional[str]]]:
        """Get bookmark status from cache."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT last_status, consecutive_failures, last_final_url
                FROM bookmarks WHERE id = ?
            """, (bookmark_id,))
            row = cursor.fetchone()
            return row if row else None
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    @retry_on_locked
    def update_status(
        self,
        bookmark_id: str,
        status: str,
        final_url: Optional[str] = None
    ) -> None:
        """Update bookmark status in cache."""
        if status is None:
            raise ValueError("status cannot be None")
            
        conn = self._get_connection()
        try:
            # Get current state
            cursor = conn.execute("""
                SELECT last_status, consecutive_failures
                FROM bookmarks WHERE id = ?
            """, (bookmark_id,))
            row = cursor.fetchone()
            
            if row:
                last_status, consecutive_failures = row
                if status == "dead":
                    consecutive_failures = (
                        consecutive_failures + 1 if last_status == "dead" else 1
                    )
                else:
                    consecutive_failures = 0
            else:
                consecutive_failures = 1 if status == "dead" else 0
            
            # Update cache
            conn.execute("""
                INSERT OR REPLACE INTO bookmarks (
                    id, last_status, consecutive_failures, last_final_url, updated_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                bookmark_id,
                status,
                consecutive_failures,
                final_url,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    def should_mark_dead(self, bookmark_id: str) -> bool:
        """Check if bookmark should be marked as dead (2+ consecutive failures)."""
        status = self.get_status(bookmark_id)
        if not status:
            return False
        
        _, consecutive_failures, _ = status
        return consecutive_failures >= 2
    
    def get_final_url(self, bookmark_id: str) -> Optional[str]:
        """Get the final URL for a bookmark after redirection."""
        status = self.get_status(bookmark_id)
        if not status:
            return None
        return status[2]

    @retry_on_locked
    def clear(self) -> None:
        """Clear all entries from the cache."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM bookmarks")
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()
    
    @retry_on_locked
    def cleanup_old_entries(self, days: int = 30) -> None:
        """Clean up entries older than specified days."""
        conn = self._get_connection()
        try:
            conn.execute(
                "DELETE FROM bookmarks WHERE updated_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()