"""Memory pipeline — SQLite storage (Hippocampus region).

Stores conversation history, user facts, notes, and reminders.
Async via aiosqlite with sync sqlite3 fallback.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any, Optional

from jarvis.core.config import config as app_config


class MemoryPipeline:
    """Persistent storage backed by SQLite.

    Provides conversation history, key-value memory, notes, and reminders
    with async interface (aiosqlite) and sync fallback.
    """

    def __init__(self, db_path: str | None = None) -> None:
        self.path = db_path or app_config.database_path
        self._conn: Any = None

    async def initialize(self) -> None:
        """Open database connection and create tables."""
        try:
            import aiosqlite
            self._conn = await aiosqlite.connect(self.path)
            self._conn.row_factory = aiosqlite.Row
            await self._conn.execute("PRAGMA journal_mode=WAL")
            await self._create_tables_async()
        except ImportError:
            self._conn = sqlite3.connect(self.path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._create_tables_sync()

    async def _create_tables_async(self) -> None:
        assert self._conn is not None
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
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL
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
        """)
        await self._conn.commit()

    def _create_tables_sync(self) -> None:
        assert self._conn is not None
        self._conn.executescript("""
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
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL
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
        """)
        self._conn.commit()

    def _is_async(self) -> bool:
        """Check if connection is async (aiosqlite) or sync (sqlite3)."""
        return "aiosqlite" in type(self._conn).__module__ if self._conn else False

    async def _execute(self, sql: str, params: tuple = ()) -> Any:
        """Execute a write query."""
        if self._is_async():
            cur = await self._conn.execute(sql, params)
            await self._conn.commit()
            return cur.lastrowid
        cur = self._conn.execute(sql, params)
        self._conn.commit()
        return cur.lastrowid

    async def _fetch(self, sql: str, params: tuple = ()) -> list[dict]:
        """Fetch rows as list of dicts."""
        if self._is_async():
            cur = await self._conn.execute(sql, params)
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
        cur = self._conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

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

    async def close(self) -> None:
        """Close database connection."""
        if not self._conn:
            return
        if self._is_async():
            await self._conn.close()
        else:
            self._conn.close()
        self._conn = None
