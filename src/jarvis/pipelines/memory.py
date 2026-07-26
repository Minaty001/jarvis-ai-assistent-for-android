"""Memory pipeline — SQLite storage (Hippocampus region).

Stores conversation history, user facts, notes, and reminders.
Uses aiosqlite. Crafted by Minaty001.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from jarvis.core.config import config as app_config


class MemoryPipeline:
    """Persistent storage backed by SQLite via aiosqlite."""

    def __init__(self, db_path: str | None = None) -> None:
        self.path = db_path or app_config.database_path
        self._conn: Any = None

    async def initialize(self) -> None:
        """Open database connection and create tables."""
        import aiosqlite

        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                session_id TEXT NOT NULL DEFAULT 'default'
            );
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                remind_at TEXT,
                done INTEGER NOT NULL DEFAULT 0,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS location_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                provider TEXT NOT NULL DEFAULT 'gps',
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS custom_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_phrase TEXT NOT NULL UNIQUE,
                actions TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        await self._conn.commit()

    async def _execute(self, sql: str, params: tuple = ()) -> Any:
        """Execute a write query."""
        cur = await self._conn.execute(sql, params)
        await self._conn.commit()
        return cur.lastrowid

    async def _fetch(self, sql: str, params: tuple = ()) -> list[dict]:
        """Fetch rows as list of dicts."""
        cur = await self._conn.execute(sql, params)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

    async def save_exchange(self, role: str, content: str) -> None:
        """Save a conversation turn."""
        await self._execute(
            "INSERT INTO conversation (role, content, session_id) VALUES (?, ?, ?)",
            (role, content, datetime.now().strftime("%Y%m%d")),
        )

    async def load_recent(self, limit: int = 20) -> list[dict]:
        """Load the most recent conversation exchanges in chronological order."""
        rows = await self._fetch(
            "SELECT role, content FROM conversation ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows.reverse()
        return rows

    async def remember(self, key: str, value: str) -> None:
        """Store or update a user fact."""
        await self._execute(
            "INSERT INTO memory (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, timestamp=datetime('now')",
            (key.lower().strip(), value),
        )

    async def recall(self, key: str) -> Optional[str]:
        """Retrieve a stored fact by key."""
        rows = await self._fetch(
            "SELECT value FROM memory WHERE key = ?", (key.lower().strip(),)
        )
        return rows[0]["value"] if rows else None

    async def get_facts(self) -> str:
        """Return all stored facts as a formatted string for LLM context."""
        rows = await self._fetch("SELECT key, value FROM memory ORDER BY timestamp DESC")
        if not rows:
            return ""
        return "\n".join(f"- {r['key']}: {r['value']}" for r in rows)

    async def save_note(self, title: str, content: str) -> int:
        """Save a new note."""
        return await self._execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title.strip(), content.strip()),
        )

    async def get_notes(self) -> list[dict]:
        """Fetch all stored notes."""
        return await self._fetch("SELECT id, title, content, timestamp FROM notes ORDER BY id DESC")

    async def delete_note(self, query: str) -> bool:
        """Delete note(s) matching title or content query."""
        if not self._conn or not query or not query.strip():
            return False
        q = query.lower().strip()
        cur = await self._conn.execute(
            "DELETE FROM notes WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?",
            (f"%{q}%", f"%{q}%"),
        )
        await self._conn.commit()
        return cur.rowcount > 0

    async def save_reminder(self, text: str, remind_at: str | None = None) -> int:
        """Save a new reminder."""
        return await self._execute(
            "INSERT INTO reminders (text, remind_at) VALUES (?, ?)",
            (text.strip(), remind_at),
        )

    async def get_reminders(self) -> list[dict]:
        """Fetch all active reminders."""
        return await self._fetch("SELECT id, text, remind_at, done, timestamp FROM reminders WHERE done = 0 ORDER BY id DESC")

    async def delete_reminder(self, query: str) -> bool:
        """Delete reminder(s) matching text query or set done."""
        if not self._conn or not query or not query.strip():
            return False
        q = query.lower().strip()
        cur = await self._conn.execute(
            "DELETE FROM reminders WHERE LOWER(text) LIKE ?",
            (f"%{q}%",),
        )
        await self._conn.commit()
        return cur.rowcount > 0

    async def save_clipboard(self, content: str) -> int:
        """Save a clipboard snippet to history."""
        return await self._execute(
            "INSERT INTO clipboard_history (content) VALUES (?)",
            (content.strip(),),
        )

    async def get_recent_clipboard(self, limit: int = 5) -> list[dict]:
        """Fetch recent clipboard entries."""
        return await self._fetch("SELECT id, content, timestamp FROM clipboard_history ORDER BY id DESC LIMIT ?", (limit,))

    async def save_location(self, latitude: float, longitude: float, provider: str = "gps") -> int:
        """Log device GPS location."""
        return await self._execute(
            "INSERT INTO location_log (latitude, longitude, provider) VALUES (?, ?, ?)",
            (latitude, longitude, provider),
        )

    async def get_last_location(self) -> Optional[dict]:
        """Fetch the most recent logged device location."""
        rows = await self._fetch("SELECT latitude, longitude, provider, timestamp FROM location_log ORDER BY id DESC LIMIT 1")
        return rows[0] if rows else None

    async def build_context(self, user_message: str) -> tuple[str, list[dict]]:
        """Build system prompt + message history for the LLM.

        Returns:
            Tuple of (system_prompt_with_facts, messages_list).
        """
        facts = await self.get_facts()
        history = await self.load_recent()

        system_prompt = (
            "You are JARVIS, an AI assistant inspired by Tony Stark's Jarvis. "
            "You are friendly, professional, witty, and respectful. "
            "You speak concisely and conversationally. "
            "You help with Android tasks, answer questions, and remember user preferences. "
            "Keep responses brief and natural — this is a voice conversation."
        )
        if facts:
            system_prompt += f"\n\nWhat I know about the user:\n{facts}"

        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        return system_prompt, messages

    async def add_custom_command(self, trigger_phrase: str, actions: str) -> int:
        """Add or update a custom voice command macro."""
        if not self._conn:
            return -1
        cursor = await self._conn.execute(
            """INSERT INTO custom_commands (trigger_phrase, actions)
               VALUES (?, ?)
               ON CONFLICT(trigger_phrase) DO UPDATE SET actions = excluded.actions""",
            (trigger_phrase.strip().lower(), actions.strip()),
        )
        await self._conn.commit()
        return cursor.lastrowid or 0

    async def get_custom_command(self, trigger_phrase: str) -> Optional[str]:
        """Fetch action sequence for a custom command trigger phrase."""
        if not self._conn:
            return None
        cursor = await self._conn.execute(
            "SELECT actions FROM custom_commands WHERE trigger_phrase = ?",
            (trigger_phrase.strip().lower(),),
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    async def list_custom_commands(self) -> list[dict]:
        """List all custom voice commands."""
        if not self._conn:
            return []
        cursor = await self._conn.execute(
            "SELECT trigger_phrase, actions FROM custom_commands ORDER BY trigger_phrase"
        )
        rows = await cursor.fetchall()
        return [{"trigger_phrase": r[0], "actions": r[1]} for r in rows]

    async def delete_custom_command(self, trigger_phrase: str) -> bool:
        """Delete a custom voice command."""
        if not self._conn or not trigger_phrase or not trigger_phrase.strip():
            return False
        cursor = await self._conn.execute(
            "DELETE FROM custom_commands WHERE trigger_phrase = ?",
            (trigger_phrase.strip().lower(),),
        )
        await self._conn.commit()
        return cursor.rowcount > 0

    async def close(self) -> None:
        """Close database connection."""
        if not self._conn:
            return
        await self._conn.close()
        self._conn = None
