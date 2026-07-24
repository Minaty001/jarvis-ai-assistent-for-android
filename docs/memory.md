# Memory Pipeline — Hippocampus

## Overview

The Memory pipeline (`pipelines/memory.py`) provides persistent storage for the Jarvis assistant. It is the **Hippocampus** cortical region — responsible for encoding, storing, and retrieving information across sessions.

Backed by SQLite with an async interface (`aiosqlite`) and a synchronous fallback (`sqlite3`).

## Database Schema

The database (`data/jarvis.db`) contains five tables:

### `conversation`

Stores the full chat history.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | Row ID |
| `role` | TEXT | `"user"` or `"assistant"` |
| `content` | TEXT | Message text |
| `timestamp` | TEXT DEFAULT `datetime('now')` | ISO-8601 timestamp |
| `session_id` | TEXT DEFAULT `'default'` | Session grouping (currently date-based) |

### `memory`

Key-value store for user facts (e.g. "my name is Alex").

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | Row ID |
| `key` | TEXT UNIQUE | Fact key (lowercase) |
| `value` | TEXT | Fact value |
| `timestamp` | TEXT DEFAULT `datetime('now')` | Last updated |

Uses `ON CONFLICT(key) DO UPDATE` — storing the same key overwrites the previous value.

### `settings`

General-purpose key-value settings store.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | Row ID |
| `key` | TEXT UNIQUE | Setting key |
| `value` | TEXT | Setting value |

### `notes`

User notes with titles.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | Row ID |
| `title` | TEXT | Note title |
| `content` | TEXT | Note body |
| `timestamp` | TEXT DEFAULT `datetime('now')` | Creation timestamp |

### `reminders`

User reminders.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | Row ID |
| `text` | TEXT | Reminder description |
| `remind_at` | TEXT | Optional due date/time |
| `done` | INTEGER DEFAULT 0 | 0 = pending, 1 = completed |
| `timestamp` | TEXT DEFAULT `datetime('now')` | Creation timestamp |

## API

```python
class MemoryPipeline:
    async def initialize() -> None
    """Open database, create tables, enable WAL mode."""

    async def save_exchange(role: str, content: str) -> None
    """Save a conversation turn (user or assistant)."""

    async def load_recent(limit: int = 20) -> list[dict]
    """Load most recent conversation turns in chronological order."""

    async def remember(key: str, value: str) -> None
    """Store or update a user fact (upsert by key)."""

    async def recall(key: str) -> str | None
    """Retrieve a stored fact by key."""

    async def get_facts() -> str
    """Return all stored facts as a formatted string for LLM prompts."""

    async def build_context(user_message: str) -> tuple[str, list[dict]]
    """Build system prompt with facts + message history for the LLM."""

    async def close() -> None
    """Close database connection."""
```

## Context Building

`build_context()` is the primary integration point with the LLM. It:

1. Loads all stored facts via `get_facts()`
2. Loads recent conversation history via `load_recent()`
3. Injects facts into the system prompt
4. Returns `(system_prompt, messages_list)` ready for `ChatPipeline.generate()`

This ensures the LLM is always aware of user preferences and prior conversation context.

## Usage Example

```python
memory = MemoryPipeline()
await memory.initialize()

# Store a fact
await memory.remember("name", "Minaty001")

# Save a conversation
await memory.save_exchange("user", "what's my name?")
await memory.save_exchange("assistant", "Your name is Minaty001.")

# Build LLM context
prompt, messages = await memory.build_context("what's my name?")
# prompt includes: "What I know about the user:\n- name: Minaty001"

# Recall a specific fact
name = await memory.recall("name")  # "Minaty001"
```

## Graceful Degradation

If `aiosqlite` is not installed, the pipeline falls back to `sqlite3` (stdlib). If the database cannot be opened or written to, errors are logged and the conversation continues without persistence — the assistant remains functional.
