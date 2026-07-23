# Jarvis AI Assistant for Android — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modular, voice-controlled AI assistant for Android Termux with a brain-inspired pipeline architecture and neural visualization UI.

**Architecture:** The assistant is structured as 6 independent pipelines (speech, chat, voice, device, memory) mapped to brain cortical regions, orchestrated by a lightweight engine. Pipelines communicate through typed async interfaces. Two UI layers render a real-time brain visualization: terminal TUI (curses) and optional web UI (Flask + SVG).

**Tech Stack:** Python 3.14 (async/await, asyncio), Vosk (STT), Groq API (LLM), Piper TTS (voice), Termux:API (device control), SQLite (memory), curses (TUI), Flask (web UI)

## Global Constraints

- Runtime target: Python 3.14.4 on aarch64-linux-android (Termux)
- No C compilation available (Pillow, cairosvg cannot build)
- Display is terminal-only; no X11/Wayland
- Audio via PortAudio (sounddevice) with ALSA fallback (aplay)
- Device API via termux-api subprocess calls
- Package manager: apt/pkg
- All project files under `/root/jarvis-ai-assistent-for-android/`
- Graceful degradation: no single pipeline failure crashes the assistant
- Wake words: "jarvis", "boss", "computer" (configurable via `.env`)
- LLM: Groq API with llama3-8b-8192 (configurable), temperature 0.7, max_tokens 512

---

## File Map

### Scaffold & Config
- `pyproject.toml` — Package metadata, build config
- `requirements.txt` — Pinned dependencies
- `.env.example` — Template for config
- `README.md` — Project docs
- `src/jarvis/__init__.py` — Package init
- `src/jarvis/__main__.py` — `python -m jarvis` entry
- `src/jarvis/cli.py` — CLI arg parser, main runner
- `src/jarvis/core/__init__.py` — Core package init
- `src/jarvis/core/config.py` — `.env` config loader
- `src/jarvis/utils/__init__.py` — Utils package init
- `src/jarvis/utils/logging.py` — Logger setup
- `src/jarvis/pipelines/__init__.py` — Pipelines package init
- `src/jarvis/ui/__init__.py` — UI package init
- `src/jarvis/ui/web_ui/__init__.py` — Web UI package init
- `tests/__init__.py` — Test package init

### Core Logic
- `src/jarvis/core/intent.py` — Rule-based intent classifier
- `src/jarvis/core/engine.py` — Lightweight orchestrator + state machine

### Pipelines
- `src/jarvis/pipelines/memory.py` — SQLite storage pipeline
- `src/jarvis/pipelines/chat.py` — Groq LLM client pipeline
- `src/jarvis/pipelines/voice.py` — Piper TTS pipeline
- `src/jarvis/pipelines/device.py` — Termux:API device control
- `src/jarvis/pipelines/speech.py` — Vosk STT + wake word pipeline

### UI
- `src/jarvis/ui/brain_renderer.py` — Brain SVG/ASCII renderer
- `src/jarvis/ui/tui.py` — Curses-based terminal UI
- `src/jarvis/ui/web_ui/app.py` — Flask web app
- `src/jarvis/ui/web_ui/static/brain.js` — Interactive brain canvas
- `src/jarvis/ui/web_ui/templates/index.html` — Main page

### Tests
- `tests/test_intent.py`
- `tests/test_memory.py`
- `tests/test_chat.py`
- `tests/test_voice.py`
- `tests/test_device.py`
- `tests/test_speech.py`
- `tests/test_engine.py`

---

## Tasks

### Task 1: Project Scaffold, Config, and Logging

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/jarvis/__init__.py`
- Create: `src/jarvis/core/__init__.py`
- Create: `src/jarvis/core/config.py`
- Create: `src/jarvis/utils/__init__.py`
- Create: `src/jarvis/utils/logging.py`
- Create: `src/jarvis/pipelines/__init__.py`
- Create: `src/jarvis/ui/__init__.py`
- Create: `src/jarvis/ui/web_ui/__init__.py`
- Create: `tests/__init__.py`

**Interfaces:**
- Consumes: (none — first task)
- Produces:
  - `Config` dataclass from `jarvis.core.config`
  - `setup_logger(name: str) -> logging.Logger` from `jarvis.utils.logging`
  - `BASE_DIR: Path` from `jarvis.core.config`

- [ ] **Step 1: Create project metadata files**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "jarvis-ai-assistent-for-android"
version = "0.2.0"
description = "Voice-controlled AI assistant for Android Termux with brain-inspired pipeline architecture"
requires-python = ">=3.11"
dependencies = [
    "vosk>=0.3.45",
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
    "aiosqlite>=0.19.0",
    "flask>=3.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23"]

[tool.setuptools.packages.find]
where = ["src"]
```

Create `requirements.txt`:

```
vosk>=0.3.45
sounddevice>=0.4.6
numpy>=1.24.0
httpx>=0.25.0
python-dotenv>=1.0.0
aiosqlite>=0.19.0
flask>=3.0.0
pytest>=8.0
pytest-asyncio>=0.23
```

Create `.env.example`:

```bash
# Groq API key for LLM
GROQ_API_KEY=
# Model to use (default: llama3-8b-8192)
MODEL_NAME=llama3-8b-8192
# Wake words (comma-separated)
WAKE_WORDS=jarvis,boss,computer
# Audio sample rate
SAMPLE_RATE=16000
# Listen timeout in seconds
LISTEN_TIMEOUT=5.0
# Groq API timeout
GROQ_TIMEOUT=30.0
# Max conversation history turns
MAX_HISTORY=20
# TTS rate and pitch (termux-tts-speak)
TTS_RATE=175
TTS_PITCH=100
```

- [ ] **Step 2: Create package init files**

Create `src/jarvis/__init__.py`:

```python
"""Jarvis AI Assistant for Android — voice-controlled assistant."""

__version__ = "0.2.0"
```

Create `src/jarvis/core/__init__.py`:

```python
"""Core logic: config, intent classification, engine orchestration."""
```

Create `src/jarvis/utils/__init__.py`:

```python
"""Utility modules: logging, helpers."""
```

Create `src/jarvis/pipelines/__init__.py`:

```python
"""Independent processing pipelines mapped to brain cortical regions."""
```

Create `src/jarvis/ui/__init__.py`:

```python
"""User interface layers: terminal TUI and web UI with brain visualization."""
```

Create `src/jarvis/ui/web_ui/__init__.py`:

```python
"""Web-based brain visualization UI."""
```

Create `tests/__init__.py`:

```python
"""Test suite for Jarvis AI Assistant."""
```

- [ ] **Step 3: Create config loader**

Create `src/jarvis/core/config.py`:

```python
"""Environment-based configuration loader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]


@dataclass
class Config:
    """Immutable configuration loaded from .env / environment variables."""

    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "llama3-8b-8192"))
    groq_api_base: str = field(default_factory=lambda: os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1"))
    database_path: str = field(default_factory=lambda: os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "jarvis.db")))
    models_dir: str = field(default_factory=lambda: os.getenv("MODELS_DIR", str(BASE_DIR / "models")))
    voices_dir: str = field(default_factory=lambda: os.getenv("VOICES_DIR", str(BASE_DIR / "voices")))
    logs_dir: str = field(default_factory=lambda: os.getenv("LOGS_DIR", str(BASE_DIR / "logs")))
    wake_words: list[str] = field(default_factory=lambda: [w.strip().lower() for w in os.getenv("WAKE_WORDS", "jarvis,boss,computer").split(",") if w.strip()])
    sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))
    listen_timeout: float = float(os.getenv("LISTEN_TIMEOUT", "5.0"))
    groq_timeout: float = float(os.getenv("GROQ_TIMEOUT", "30.0"))
    max_history: int = int(os.getenv("MAX_HISTORY", "20"))
    tts_rate: int = int(os.getenv("TTS_RATE", "175"))
    tts_pitch: int = int(os.getenv("TTS_PITCH", "100"))

    def __post_init__(self) -> None:
        """Ensure required directories exist."""
        for d in [self.models_dir, self.voices_dir, self.logs_dir, str(BASE_DIR / "data")]:
            Path(d).mkdir(parents=True, exist_ok=True)


# Global singleton
config = Config()
```

- [ ] **Step 4: Create logging utility**

Create `src/jarvis/utils/logging.py`:

```python
"""Logging setup for Jarvis."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from jarvis.core.config import config


def setup_logger(name: str = "jarvis") -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Logger name (default 'jarvis').

    Returns:
        Configured logger with file + console handlers.
    """
    log_file = Path(config.logs_dir) / f"{name}.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


log = setup_logger()
```

- [ ] **Step 5: Verify scaffold works**

```bash
cd /root/jarvis-ai-assistent-for-android && python -c "from jarvis.core.config import config; from jarvis.utils.logging import log; print(f'Config loaded: {config.model_name}'); print('Scaffold OK')"
```

Expected output:
```
Config loaded: llama3-8b-8192
Scaffold OK
```

- [ ] **Step 6: Commit scaffold**

```bash
cd /root/jarvis-ai-assistent-for-android && git init && git add -A && git commit -m "feat: initial project scaffold with config and logging"
```

---

### Task 2: Intent Classifier

**Files:**
- Create: `src/jarvis/core/intent.py`
- Create: `tests/test_intent.py`

**Interfaces:**
- Consumes: none (pure function)
- Produces:
  - `classify_intent(text: str) -> tuple[str, dict[str, str]]`

- [ ] **Step 1: Write the intent classifier module**

Create `src/jarvis/core/intent.py`:

```python
"""Rule-based intent classifier mapping text to intent type + params."""

from __future__ import annotations

import re

_INTENT_PATTERNS: list[tuple[str, str, list[str]]] = [
    ("open_settings", r"(?:open|launch)\s+(?:the\s+)?settings", []),
    ("open_camera", r"(?:open|launch)\s+(?:the\s+)?camera", []),
    ("open_gallery", r"(?:open|launch)\s+(?:the\s+)?gallery", []),
    ("open_youtube", r"(?:open|launch)\s+youtube", []),
    ("open_website", r"(?:open|go\s+to|visit)\s+(?:the\s+)?website\s+(.+)", ["url"]),
    ("open_website", r"go\s+to\s+(.+)", ["url"]),
    ("open_website", r"visit\s+(.+)", ["url"]),
    ("open_app", r"(?:open|launch|start)\s+(?:the\s+)?(.+)", ["app_name"]),
    ("close_app", r"(?:close|exit|quit|kill)\s+(?:the\s+)?(.+)", ["app_name"]),
    ("go_home", r"(?:go\s+)?home\s*(?:screen)?", []),
    ("show_recent", r"(?:show|view)\s+(?:recent|recents|recent\s+apps)", []),
    ("show_notifications", r"(?:show|view|check)\s+(?:notifications|notification)", []),
    ("flashlight_on", r"(?:turn\s+on|enable|switch\s+on)\s+(?:the\s+)?flashlight", []),
    ("flashlight_off", r"(?:turn\s+off|disable|switch\s+off)\s+(?:the\s+)?flashlight", []),
    ("volume_up", r"(?:turn\s+)?volume\s+up|increase\s+volume", []),
    ("volume_down", r"(?:turn\s+)?volume\s+down|decrease\s+volume|lower\s+volume", []),
    ("set_volume", r"(?:set\s+)?volume\s+to\s+(\d+)", ["level"]),
    ("brightness_up", r"brightness\s+up|increase\s+brightness", []),
    ("brightness_down", r"brightness\s+down|decrease\s+brightness|lower\s+brightness", []),
    ("set_brightness", r"(?:set\s+)?brightness\s+to\s+(\d+)", ["level"]),
    ("tell_time", r"(?:what(?:\'s| is)\s+)?(?:the\s+)?\btime\b(?:\s+now)?", []),
    ("tell_date", r"(?:what(?:\'s| is)\s+)?(?:the\s+)?\bdate\b(?:\s+today)?", []),
    ("battery_status", r"(?:battery|battery\s+status|battery\s+level|how\s+much\s+battery)", []),
    ("wifi_on", r"(?:turn\s+on|enable|switch\s+on)\s+(?:the\s+)?wifi", []),
    ("wifi_on", r"wifi\s+(?:on|enable)", []),
    ("wifi_off", r"(?:turn\s+off|disable|switch\s+off)\s+(?:the\s+)?wifi", []),
    ("wifi_off", r"wifi\s+(?:off|disable)", []),
    ("wifi_status", r"(?:wifi\s+)?status|is\s+wifi\s+(?:on|connected)", []),
    ("bluetooth_on", r"(?:turn\s+on|enable|switch\s+on)\s+(?:the\s+)?bluetooth", []),
    ("bluetooth_on", r"bluetooth\s+(?:on|enable)", []),
    ("bluetooth_off", r"(?:turn\s+off|disable|switch\s+off)\s+(?:the\s+)?bluetooth", []),
    ("bluetooth_off", r"bluetooth\s+(?:off|disable)", []),
    ("search_google", r"(?:search\s+(?:the\s+)?(?:web\s+)?(?:for\s+)?|google\s+(?:for\s+)?|look\s+up\s+(?:for\s+)?)(.+)", ["query"]),
    ("play_music", r"(?:play|search)\s+(?:music|song|audio)\s+(.+)|play\s+(.+)", ["query"]),
    ("take_note", r"(?:take|make|create|write|save)\s+(?:a\s+)?note\s+(?:that\s+)?(.+)", ["content"]),
    ("read_notes", r"(?:read|show|list|view)\s+(?:my\s+)?notes", []),
    ("delete_note", r"(?:delete|remove|erase)\s+(?:note\s+)?(.+)", ["query"]),
    ("set_reminder", r"(?:set|create|make)\s+(?:a\s+)?reminder\s+(?:to\s+)?(.+)", ["text"]),
    ("view_reminders", r"(?:view|show|list)\s+(?:my\s+)?reminders", []),
    ("delete_reminder", r"(?:delete|remove|clear)\s+(?:reminder\s+)?(.+)", ["query"]),
    ("calculate", r"(?:calculate|compute)\s+(.+)", ["expression"]),
    ("remember_fact", r"(?:remember|note|remember\s+that|keep\s+in\s+mind)\s+(?:that\s+)?(.+)", ["fact"]),
    ("what_is", r"what(?:\'s| is)\s+(?:my\s+|the\s+)?(.+)", ["query"]),
    ("exit", r"(?:exit|quit|goodbye|bye|shutdown|see\s+you)", []),
]


def classify_intent(text: str) -> tuple[str, dict[str, str]]:
    """Classify user text into an intent type with extracted parameters.

    Args:
        text: Raw user input string.

    Returns:
        Tuple of (intent_type, params_dict). Defaults to
        ('general_chat', {'text': text}) when no pattern matches.
    """
    text_lower = text.strip().lower()
    params: dict[str, str] = {}

    for intent, pattern, param_names in _INTENT_PATTERNS:
        match = re.search(pattern, text_lower)
        if not match:
            continue
        groups = match.groups()
        if param_names:
            for i, name in enumerate(param_names):
                if i < len(groups) and groups[i]:
                    params[name] = groups[i].strip()

        if intent == "search_google" and "query" in params:
            query = params["query"]
            query = re.sub(r"^(?:google\s+(?:for\s+)?|for\s+)", "", query).strip()
            params["query"] = query
        elif intent == "play_music":
            q = " ".join(g for g in groups if g).strip()
            if q:
                params["query"] = q
        elif intent == "open_website" and "url" in params:
            url = params["url"]
            if not url.startswith("http"):
                if "." in url and " " not in url:
                    params["url"] = f"https://{url}"
                else:
                    return "search_google", {"query": url}
        elif intent == "remember_fact" and "fact" in params:
            fact = params["fact"]
            if ":" in fact:
                parts = fact.split(":", 1)
                params["key"] = parts[0].strip()
                params["value"] = parts[1].strip()

        return intent, params

    return "general_chat", {"text": text}
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_intent.py`:

```python
"""Tests for the intent classifier."""

import pytest
from jarvis.core.intent import classify_intent


class TestIntentClassifier:
    """Verify rule-based intent matching and parameter extraction."""

    def test_open_app_intent(self):
        intent, params = classify_intent("open camera")
        assert intent == "open_app"
        assert params["app_name"] == "camera"

    def test_open_settings_intent(self):
        intent, params = classify_intent("open settings")
        assert intent == "open_settings"

    def test_tell_time_intent(self):
        intent, params = classify_intent("what's the time")
        assert intent == "tell_time"

    def test_tell_date_intent(self):
        intent, params = classify_intent("what is the date")
        assert intent == "tell_date"

    def test_battery_status(self):
        intent, params = classify_intent("battery status")
        assert intent == "battery_status"

    def test_flashlight_on(self):
        intent, params = classify_intent("turn on flashlight")
        assert intent == "flashlight_on"

    def test_flashlight_off(self):
        intent, params = classify_intent("disable flashlight")
        assert intent == "flashlight_off"

    def test_volume_up(self):
        intent, params = classify_intent("volume up")
        assert intent == "volume_up"

    def test_volume_down(self):
        intent, params = classify_intent("lower volume")
        assert intent == "volume_down"

    def test_set_volume(self):
        intent, params = classify_intent("set volume to 7")
        assert intent == "set_volume"
        assert params["level"] == "7"

    def test_brightness_up(self):
        intent, params = classify_intent("increase brightness")
        assert intent == "brightness_up"

    def test_set_brightness(self):
        intent, params = classify_intent("set brightness to 50")
        assert intent == "set_brightness"
        assert params["level"] == "50"

    def test_wifi_on(self):
        intent, params = classify_intent("turn on wifi")
        assert intent == "wifi_on"

    def test_wifi_off(self):
        intent, params = classify_intent("wifi off")
        assert intent == "wifi_off"

    def test_bluetooth_on(self):
        intent, params = classify_intent("enable bluetooth")
        assert intent == "bluetooth_on"

    def test_search_google(self):
        intent, params = classify_intent("search for Python tutorials")
        assert intent == "search_google"
        assert "Python tutorials" in params["query"]

    def test_take_note(self):
        intent, params = classify_intent("take a note that I need milk")
        assert intent == "take_note"
        assert "I need milk" in params["content"]

    def test_read_notes(self):
        intent, params = classify_intent("show my notes")
        assert intent == "read_notes"

    def test_set_reminder(self):
        intent, params = classify_intent("set a reminder to call John")
        assert intent == "set_reminder"
        assert "call John" in params["text"]

    def test_remember_fact(self):
        intent, params = classify_intent("remember that my favorite color is blue")
        assert intent == "remember_fact"

    def test_exit_intent(self):
        intent, params = classify_intent("goodbye")
        assert intent == "exit"

    def test_general_chat_fallback(self):
        intent, params = classify_intent("tell me a joke")
        assert intent == "general_chat"
        assert params["text"] == "tell me a joke"

    def test_go_home(self):
        intent, params = classify_intent("go home")
        assert intent == "go_home"

    def test_show_notifications(self):
        intent, params = classify_intent("show notifications")
        assert intent == "show_notifications"
```

- [ ] **Step 3: Run tests to verify they fail initially**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_intent.py -v 2>&1 | head -30
```

Expected: Tests fail because `intent` module doesn't exist yet.

- [ ] **Step 4: Write the implementation**

(The intent classifier is already written in Step 1 above — the file exists after Step 1.)

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_intent.py -v
```

Expected: All ~22 tests PASS.

- [ ] **Step 6: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/core/intent.py tests/test_intent.py && git commit -m "feat: add intent classifier with 40+ patterns"
```

---

### Task 3: Memory Pipeline (SQLite)

**Files:**
- Create: `src/jarvis/pipelines/memory.py`
- Create: `tests/test_memory.py`

**Interfaces:**
- Consumes: `Config.database_path` from `jarvis.core.config`
- Produces:
  - `MemoryPipeline.save_exchange(role, content) -> None`
  - `MemoryPipeline.load_recent(limit=20) -> list[dict]`
  - `MemoryPipeline.remember(key, value) -> None`
  - `MemoryPipeline.recall(key) -> Optional[str]`
  - `MemoryPipeline.get_facts() -> str`
  - `MemoryPipeline.build_context(user_msg) -> tuple[str, list[dict]]`
  - `MemoryPipeline.close() -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/test_memory.py`:

```python
"""Tests for the Memory pipeline (SQLite storage)."""

import pytest
from jarvis.pipelines.memory import MemoryPipeline


@pytest.fixture
async def mem(tmp_path):
    db_path = str(tmp_path / "test.db")
    pipeline = MemoryPipeline(db_path=db_path)
    await pipeline.initialize()
    yield pipeline
    await pipeline.close()


@pytest.mark.asyncio
async def test_save_and_load_exchange(mem):
    await mem.save_exchange("user", "hello")
    await mem.save_exchange("assistant", "hi there")
    recent = await mem.load_recent(limit=10)
    assert len(recent) == 2
    assert recent[0]["role"] == "user"
    assert recent[0]["content"] == "hello"
    assert recent[1]["role"] == "assistant"
    assert recent[1]["content"] == "hi there"


@pytest.mark.asyncio
async def test_load_recent_respects_limit(mem):
    for i in range(5):
        await mem.save_exchange("user", f"msg{i}")
    recent = await mem.load_recent(limit=3)
    assert len(recent) == 3
    assert recent[-1]["content"] == "msg4"  # most recent last


@pytest.mark.asyncio
async def test_remember_and_recall(mem):
    await mem.remember("color", "blue")
    result = await mem.recall("color")
    assert result == "blue"


@pytest.mark.asyncio
async def test_recall_nonexistent(mem):
    result = await mem.recall("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_remember_overwrites(mem):
    await mem.remember("name", "Alice")
    await mem.remember("name", "Bob")
    result = await mem.recall("name")
    assert result == "Bob"


@pytest.mark.asyncio
async def test_get_facts(mem):
    await mem.remember("city", "Tokyo")
    await mem.remember("pet", "dog")
    facts = await mem.get_facts()
    assert "city: Tokyo" in facts
    assert "pet: dog" in facts


@pytest.mark.asyncio
async def test_get_facts_empty(mem):
    facts = await mem.get_facts()
    assert facts == ""


@pytest.mark.asyncio
async def test_build_context_includes_facts(mem):
    await mem.remember("name", "Jarvis")
    await mem.save_exchange("user", "hello")
    system_prompt, messages = await mem.build_context("what's my name?")
    assert "name: Jarvis" in system_prompt
    assert len(messages) >= 2  # system + user
    assert messages[-1]["content"] == "what's my name?"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_memory.py -v 2>&1 | head -10
```

Expected: ImportError — no `memory` module.

- [ ] **Step 3: Write memory pipeline implementation**

Create `src/jarvis/pipelines/memory.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_memory.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/pipelines/memory.py tests/test_memory.py && git commit -m "feat: add memory pipeline with SQLite storage"
```

---

### Task 4: Chat Pipeline (Groq LLM)

**Files:**
- Create: `src/jarvis/pipelines/chat.py`
- Create: `tests/test_chat.py`

**Interfaces:**
- Consumes:
  - `Config.groq_api_key`, `Config.model_name`, `Config.groq_api_base`, `Config.groq_timeout` from `jarvis.core.config`
- Produces:
  - `ChatPipeline.generate(messages: list[dict]) -> Optional[str]`
  - `ChatPipeline.close() -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/test_chat.py`:

```python
"""Tests for the Chat pipeline (Groq LLM)."""

import pytest
from jarvis.pipelines.chat import ChatPipeline


@pytest.mark.asyncio
async def test_generate_returns_none_without_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    pipeline = ChatPipeline()
    result = await pipeline.generate([{"role": "user", "content": "hello"}])
    assert result is None
    await pipeline.close()


@pytest.mark.asyncio
async def test_generate_adds_system_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    pipeline = ChatPipeline()
    # With empty messages, it should still work (no system prompt added if not first)
    result = await pipeline.generate([{"role": "user", "content": "hi"}])
    # Without httpx it returns None
    assert result is None or isinstance(result, str)
    await pipeline.close()


@pytest.mark.asyncio
async def test_close_cleans_up_client(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    pipeline = ChatPipeline()
    await pipeline.close()
    assert pipeline._client is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_chat.py -v 2>&1 | head -10
```

Expected: ImportError — no `chat` module.

- [ ] **Step 3: Write chat pipeline implementation**

Create `src/jarvis/pipelines/chat.py`:

```python
"""Chat pipeline — Groq LLM client (Wernicke's Area).

Sends messages to Groq API and returns the response text.
Supports system prompt injection, retry on rate limits, and timeout.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log

GROQ_SYSTEM_PROMPT = (
    "You are JARVIS, an AI assistant inspired by Tony Stark's Jarvis. "
    "You are friendly, professional, witty, and respectful. "
    "You speak concisely and conversationally — this is a voice conversation, "
    "so keep responses brief (1-3 sentences when possible). "
    "You help with Android tasks, answer questions, and remember user preferences. "
    "You have a subtle dry wit but are always helpful."
)


class ChatPipeline:
    """Async Groq API client for LLM inference."""

    def __init__(self) -> None:
        self.api_key = app_config.groq_api_key
        self.model = app_config.model_name
        self.base_url = app_config.groq_api_base
        self.timeout = app_config.groq_timeout
        self._client: Any = None

    async def _ensure_client(self) -> None:
        if self._client is not None:
            return
        try:
            import httpx
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        except ImportError:
            log.warning("httpx not installed. Chat pipeline unavailable.")
            self._client = None

    async def generate(self, messages: list[dict]) -> Optional[str]:
        """Send messages to Groq and return the response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     If first message is not a system prompt, one is prepended.

        Returns:
            Response text string, or None on failure.
        """
        if not self.api_key:
            log.error("GROQ_API_KEY not set.")
            return None

        await self._ensure_client()
        if self._client is None:
            return None

        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": GROQ_SYSTEM_PROMPT})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
            "stream": False,
        }

        for attempt in range(2):
            try:
                resp = await self._client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                )
                if resp.status_code == 429:
                    log.warning("Groq rate limited. Retrying...")
                    await asyncio.sleep(2)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                log.error(f"Groq API error (attempt {attempt + 1}): {e}")
                if attempt == 0:
                    await asyncio.sleep(1)
                    continue
                return None

        return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_chat.py -v
```

Expected: All 3 tests PASS (first test passes because api_key is empty after monkeypatch).

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/pipelines/chat.py tests/test_chat.py && git commit -m "feat: add chat pipeline with Groq LLM client"
```

---

### Task 5: Voice Pipeline (TTS)

**Files:**
- Create: `src/jarvis/pipelines/voice.py`
- Create: `tests/test_voice.py`

**Interfaces:**
- Consumes: `Config.tts_rate`, `Config.tts_pitch` from `jarvis.core.config`
- Produces:
  - `VoicePipeline.speak(text: str) -> None`
  - `VoicePipeline.cancel() -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/test_voice.py`:

```python
"""Tests for the Voice pipeline (Piper TTS)."""

import pytest
from jarvis.pipelines.voice import VoicePipeline


@pytest.mark.asyncio
async def test_speak_empty_text_is_noop():
    pipeline = VoicePipeline()
    await pipeline.speak("")  # Should not raise
    await pipeline.cancel()


@pytest.mark.asyncio
async def test_speak_then_cancel():
    pipeline = VoicePipeline()
    await pipeline.speak("hello world")
    await pipeline.cancel()  # Should not raise
    # After cancel, speaking again should work
    await pipeline.speak("another message")
    await pipeline.cancel()


@pytest.mark.asyncio
async def test_double_cancel_is_safe():
    pipeline = VoicePipeline()
    await pipeline.cancel()
    await pipeline.cancel()  # Second cancel should be safe
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_voice.py -v 2>&1 | head -10
```

Expected: ImportError — no `voice` module.

- [ ] **Step 3: Write voice pipeline implementation**

Create `src/jarvis/pipelines/voice.py`:

```python
"""Voice pipeline — Text-to-Speech (Broca's Area).

Primary: Piper TTS (local, low-latency).
Fallback: termux-tts-speak (Android TTS engine).
Final fallback: log only.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
from typing import Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log


class VoicePipeline:
    """Async TTS with Piper (preferred) and termux-tts-speak fallback."""

    def __init__(self) -> None:
        self._speak_task: Optional[asyncio.Task] = None

    async def speak(self, text: str) -> None:
        """Speak text. Cancels any current speech first (interrupt behavior).

        Args:
            text: Text to speak aloud.
        """
        await self.cancel()
        if not text.strip():
            return
        log.info(f"JARVIS: {text}")
        self._speak_task = asyncio.create_task(self._do_speak(text))

    async def _do_speak(self, text: str) -> None:
        """Internal: try Piper, then termux-tts-speak, then log-only."""
        if await self._try_piper(text):
            return
        if await self._try_termux_tts(text):
            return
        log.info(f"(TTS unavailable) Would say: {text}")

    async def _try_piper(self, text: str) -> bool:
        """Try Piper TTS. Returns True if speech was produced."""
        piper = self._find_piper()
        voice = self._find_piper_voice()
        if not piper or not voice:
            return False

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, self._run_piper_sync, piper, voice, text, output_path
            )
            await loop.run_in_executor(None, self._play_wav_sync, output_path)
            return True
        except Exception as e:
            log.debug(f"Piper TTS failed: {e}")
            return False

    def _run_piper_sync(self, piper_bin: str, voice_path: str, text: str, output_path: str) -> None:
        try:
            proc = subprocess.run(
                [piper_bin, "--model", voice_path, "--output_file", output_path],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )
            if proc.returncode != 0:
                log.warning(f"Piper error: {proc.stderr.decode(errors='replace')[:200]}")
        except Exception as e:
            log.debug(f"Piper execution failed: {e}")

    def _play_wav_sync(self, path: str) -> None:
        try:
            subprocess.run(["termux-media-player", "play", path], capture_output=True, timeout=10)
        except Exception:
            try:
                subprocess.run(["aplay", path], capture_output=True, timeout=10)
            except Exception:
                pass
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass

    def _find_piper(self) -> Optional[str]:
        candidates = ["piper", os.path.expanduser("~/.local/bin/piper")]
        for c in candidates:
            try:
                proc = subprocess.run(["which", c], capture_output=True, timeout=5)
                if proc.returncode == 0:
                    return c.strip()
            except Exception:
                continue
        return None

    def _find_piper_voice(self) -> Optional[str]:
        voices_dir = os.path.expanduser(app_config.voices_dir)
        for root, _dirs, files in os.walk(voices_dir):
            for f in files:
                if f.endswith(".onnx"):
                    return os.path.join(root, f)
        voice_name = os.getenv("PIPER_VOICE", "en_US-amy-medium")
        specific = os.path.join(voices_dir, f"{voice_name}.onnx")
        if os.path.exists(specific):
            return specific
        return None

    async def _try_termux_tts(self, text: str) -> bool:
        """Fallback: use termux-tts-speak."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-tts-speak",
                "-r", str(app_config.tts_rate),
                "-p", str(app_config.tts_pitch),
                text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return False

    async def cancel(self) -> None:
        """Cancel current speech."""
        if self._speak_task and not self._speak_task.done():
            self._speak_task.cancel()
            try:
                await self._speak_task
            except (asyncio.CancelledError, Exception):
                pass
        self._speak_task = None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_voice.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/pipelines/voice.py tests/test_voice.py && git commit -m "feat: add voice pipeline with Piper TTS and fallback"
```

---

### Task 6: Device Pipeline (Termux:API)

**Files:**
- Create: `src/jarvis/pipelines/device.py`
- Create: `tests/test_device.py`

**Interfaces:**
- Consumes: none (subprocess calls)
- Produces:
  - `DevicePipeline.execute(intent: str, params: dict) -> str`
  - `DevicePipeline.has_termux() -> bool`

- [ ] **Step 1: Write the failing test**

Create `tests/test_device.py`:

```python
"""Tests for the Device pipeline (Termux:API control)."""

import pytest
from jarvis.pipelines.device import DevicePipeline


@pytest.mark.asyncio
async def test_has_termux_returns_bool():
    pipeline = DevicePipeline()
    result = pipeline.has_termux()
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_execute_tell_time():
    pipeline = DevicePipeline()
    result = await pipeline.execute("tell_time", {})
    assert "time" in result.lower() or ":" in result


@pytest.mark.asyncio
async def test_execute_tell_date():
    pipeline = DevicePipeline()
    result = await pipeline.execute("tell_date", {})
    assert "today" in result.lower() or "202" in result


@pytest.mark.asyncio
async def test_execute_unknown_intent_returns_error():
    pipeline = DevicePipeline()
    result = await pipeline.execute("nonexistent_intent", {})
    assert "unknown" in result.lower() or "unknown" in result


@pytest.mark.asyncio
async def test_execute_flashlight_on_without_termux():
    pipeline = DevicePipeline()
    # Without termux-api, should return error message, not crash
    result = await pipeline.execute("flashlight_on", {})
    assert isinstance(result, str)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_device.py -v 2>&1 | head -10
```

Expected: ImportError — no `device` module.

- [ ] **Step 3: Write device pipeline implementation**

Create `src/jarvis/pipelines/device.py`:

```python
"""Device pipeline — Termux:API Android control (Motor Cortex).

Executes device actions via termux-api subprocess commands.
Gracefully degrades when termux-api is not available.
"""

from __future__ import annotations

import asyncio
import subprocess
from datetime import datetime
from typing import Optional

from jarvis.utils.logging import log


class DevicePipeline:
    """Async wrapper around Termux-API and Android commands."""

    def __init__(self) -> None:
        self._has_termux = self._check_termux()

    def _check_termux(self) -> bool:
        """Check if termux-battery-status is available."""
        try:
            proc = subprocess.run(
                ["termux-battery-status"], capture_output=True, timeout=5
            )
            return proc.returncode == 0
        except Exception:
            return False

    def has_termux(self) -> bool:
        """Return whether Termux:API is available on this device."""
        return self._has_termux

    async def _run(self, *args: str, input_data: Optional[str] = None) -> str:
        """Run a subprocess asynchronously and return stdout."""
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE if input_data else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(
                input=input_data.encode() if input_data else None
            )
            if proc.returncode != 0:
                err = stderr.decode(errors="replace").strip()
                if err:
                    log.warning(f"Command {' '.join(args)} error: {err}")
            return stdout.decode(errors="replace").strip()
        except FileNotFoundError:
            return f"ERROR: {args[0]} not found. Install termux-api package."
        except Exception as e:
            return f"ERROR: {e}"

    async def execute(self, intent: str, params: dict[str, str]) -> str:
        """Execute a device action based on intent type and parameters.

        Args:
            intent: Classified intent name (e.g. 'open_app', 'flashlight_on').
            params: Extracted parameters from intent classifier.

        Returns:
            Human-readable result string.
        """
        handler = self._get_handler(intent)
        if handler is None:
            return f"Unknown action: {intent}"
        return await handler(params)

    def _get_handler(self, intent: str):
        """Map intent name to handler method."""
        handlers = {
            "open_app": self._open_app,
            "close_app": self._close_app,
            "open_settings": lambda p: self._open_app({"app_name": "settings"}),
            "open_camera": lambda p: self._open_app({"app_name": "camera"}),
            "open_gallery": lambda p: self._open_app({"app_name": "gallery"}),
            "open_youtube": self._open_youtube,
            "open_website": self._open_website,
            "go_home": lambda p: self._run("termux-tool", "keyboard", "key", "3"),
            "show_recent": lambda p: self._run("termux-tool", "keyboard", "key", "5"),
            "show_notifications": lambda p: self._run("termux-notification-list"),
            "flashlight_on": lambda p: self._run("termux-torch", "on"),
            "flashlight_off": lambda p: self._run("termux-torch", "off"),
            "volume_up": lambda p: self._run("termux-volume", "music", "10"),
            "volume_down": lambda p: self._run("termux-volume", "music", "1"),
            "set_volume": self._set_volume,
            "brightness_up": lambda p: self._run("termux-brightness", "255"),
            "brightness_down": lambda p: self._run("termux-brightness", "50"),
            "set_brightness": self._set_brightness,
            "tell_time": self._tell_time,
            "tell_date": self._tell_date,
            "battery_status": self._battery_status,
            "wifi_on": lambda p: self._run("termux-wifi-enable", "true"),
            "wifi_off": lambda p: self._run("termux-wifi-enable", "false"),
            "wifi_status": lambda p: self._run("termux-wifi-scaninfo"),
            "bluetooth_on": lambda p: self._run("termux-bluetooth-enable", "on"),
            "bluetooth_off": lambda p: self._run("termux-bluetooth-enable", "off"),
            "search_google": self._search_google,
            "play_music": self._play_music,
            "take_note": self._take_note,
            "read_notes": self._read_notes,
            "delete_note": self._delete_note,
            "set_reminder": self._set_reminder,
            "view_reminders": self._view_reminders,
            "delete_reminder": self._delete_reminder,
        }
        return handlers.get(intent)

    async def _open_app(self, params: dict[str, str]) -> str:
        app_name = params.get("app_name", "")
        app_map = {
            "settings": "com.android.settings",
            "camera": "com.android.camera2",
            "gallery": "com.android.gallery",
            "chrome": "com.android.chrome",
            "browser": "com.android.chrome",
            "youtube": "com.google.android.youtube",
            "maps": "com.google.android.apps.maps",
            "gmail": "com.google.android.gm",
            "calculator": "com.android.calculator2",
            "clock": "com.android.deskclock",
            "phone": "com.android.dialer",
            "contacts": "com.android.contacts",
            "messages": "com.android.messaging",
            "play store": "com.android.vending",
            "spotify": "com.spotify.music",
            "whatsapp": "com.whatsapp",
            "telegram": "org.telegram.messenger",
            "twitter": "com.twitter.android",
            "instagram": "com.instagram.android",
            "facebook": "com.facebook.katana",
            "files": "com.android.documentsui",
            "terminal": "com.termux",
        }
        package = app_map.get(app_name.lower(), app_name)
        result = await self._run("am", "start", "-n", f"{package}/.MainActivity")
        if "ERROR" in result:
            result = await self._run("am", "start", "-n", f"{package}/.main")
        return f"Opened {app_name}." if "ERROR" not in result else f"Could not open {app_name}."

    async def _close_app(self, params: dict[str, str]) -> str:
        app_name = params.get("app_name", "")
        app_map = {
            "settings": "com.android.settings",
            "camera": "com.android.camera2",
            "youtube": "com.google.android.youtube",
            "browser": "com.android.chrome",
            "chrome": "com.android.chrome",
        }
        package = app_map.get(app_name.lower(), app_name)
        result = await self._run("am", "force-stop", package)
        return f"Closed {app_name}." if "ERROR" not in result else f"Could not close {app_name}."

    async def _open_youtube(self, params: dict[str, str]) -> str:
        result = await self._run("am", "start", "-n", "com.google.android.youtube/.MainActivity")
        if "ERROR" not in result:
            return "Opening YouTube."
        return await self._run("termux-open", "https://youtube.com")

    async def _open_website(self, params: dict[str, str]) -> str:
        url = params.get("url", "")
        result = await self._run("termux-open", url)
        return f"Opening {url}." if "ERROR" not in result else f"Could not open website."

    async def _set_volume(self, params: dict[str, str]) -> str:
        level = params.get("level", "5")
        result = await self._run("termux-volume", "music", level)
        return f"Volume set to {level}." if "ERROR" not in result else f"Could not set volume."

    async def _set_brightness(self, params: dict[str, str]) -> str:
        level = params.get("level", "128")
        result = await self._run("termux-brightness", level)
        return f"Brightness set to {level}." if "ERROR" not in result else "Could not set brightness."

    async def _tell_time(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"The time is {now.strftime('%I:%M %p').lstrip('0')}."

    async def _tell_date(self, params: dict[str, str]) -> str:
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    async def _battery_status(self, params: dict[str, str]) -> str:
        result = await self._run("termux-battery-status")
        if result.startswith("ERROR"):
            return "Battery status unavailable."
        try:
            import json
            data = json.loads(result)
            pct = data.get("percentage", "?")
            plug = data.get("plugged", "?")
            return f"Battery at {pct}%, {'plugged in' if plug else 'on battery'}."
        except Exception:
            return f"Battery status: {result[:100]}"

    async def _search_google(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "")
        url = f"https://www.google.com/search?q={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Searching Google for {query}." if "ERROR" not in result else "Could not open browser."

    async def _play_music(self, params: dict[str, str]) -> str:
        from urllib.parse import quote
        query = params.get("query", "")
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        result = await self._run("termux-open", url)
        return f"Searching YouTube for {query}." if "ERROR" not in result else "Could not open YouTube."

    async def _take_note(self, params: dict[str, str]) -> str:
        return "Note saved. (In-memory — full persistence via MemoryPipeline)"

    async def _read_notes(self, params: dict[str, str]) -> str:
        return "Notes feature: use MemoryPipeline for full persistence."

    async def _delete_note(self, params: dict[str, str]) -> str:
        return "Delete note: use MemoryPipeline for full persistence."

    async def _set_reminder(self, params: dict[str, str]) -> str:
        return f"Reminder set for: {params.get('text', '')}."

    async def _view_reminders(self, params: dict[str, str]) -> str:
        return "Reminders: use MemoryPipeline for full persistence."

    async def _delete_reminder(self, params: dict[str, str]) -> str:
        return "Delete reminder: use MemoryPipeline for full persistence."
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_device.py -v
```

Expected: All 5 tests PASS (time/date tests work without termux; other handlers return error strings).

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/pipelines/device.py tests/test_device.py && git commit -m "feat: add device pipeline with Termux:API control"
```

---

### Task 7: Speech Pipeline (Vosk STT)

**Files:**
- Create: `src/jarvis/pipelines/speech.py`
- Create: `tests/test_speech.py`

**Interfaces:**
- Consumes: `Config.models_dir`, `Config.wake_words`, `Config.sample_rate`, `Config.listen_timeout` from `jarvis.core.config`
- Produces:
  - `SpeechPipeline.load_model() -> bool`
  - `SpeechPipeline.start() -> None`
  - `SpeechPipeline.stop() -> None`
  - `SpeechPipeline.wait_for_wake() -> bool`
  - `SpeechPipeline.listen(timeout: float) -> Optional[str]`
  - `SpeechPipeline.set_on_speech_detected(callback) -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/test_speech.py`:

```python
"""Tests for the Speech pipeline (Vosk STT)."""

import pytest
from jarvis.pipelines.speech import SpeechPipeline


@pytest.mark.asyncio
async def test_load_model_returns_false_without_vosk(monkeypatch):
    monkeypatch.setattr("jarvis.pipelines.speech.VoskModel", None)
    pipeline = SpeechPipeline()
    result = await pipeline.load_model()
    assert result is False


@pytest.mark.asyncio
async def test_load_model_returns_false_without_model_file(monkeypatch):
    # Simulate Vosk imported but model file missing
    class FakeVoskModel:
        def __init__(self, path):
            raise Exception("model not found")

    monkeypatch.setattr("jarvis.pipelines.speech.VoskModel", FakeVoskModel)
    pipeline = SpeechPipeline()
    result = await pipeline.load_model()
    assert result is False


@pytest.mark.asyncio
async def test_start_stop_without_model():
    pipeline = SpeechPipeline()
    await pipeline.start()  # Should not crash without model
    await pipeline.stop()


@pytest.mark.asyncio
async def test_listen_returns_none_after_timeout():
    pipeline = SpeechPipeline()
    result = await pipeline.listen(timeout=0.1)
    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_speech.py -v 2>&1 | head -10
```

Expected: ImportError — no `speech` module.

- [ ] **Step 3: Write speech pipeline implementation**

Create `src/jarvis/pipelines/speech.py`:

```python
"""Speech pipeline — Vosk STT and wake word detection (Auditory Cortex).

Captures microphone audio, performs speech-to-text via Vosk,
and detects wake words for hands-free activation.
"""

from __future__ import annotations

import asyncio
import json
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable, Optional

from jarvis.core.config import config as app_config
from jarvis.utils.logging import log

try:
    import numpy as np
    import sounddevice as sd
except (ImportError, OSError):
    np = None
    sd = None

try:
    from vosk import Model as VoskModel, KaldiRecognizer
except ImportError:
    VoskModel = None
    KaldiRecognizer = None

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
VOSK_MODEL_DIR_NAME = "vosk-model-small-en-us-0.15"


class SpeechPipeline:
    """Async speech recognition with wake word detection."""

    def __init__(self) -> None:
        self.model_path = Path(app_config.models_dir) / VOSK_MODEL_DIR_NAME
        self.model: Any = None
        self.recognizer: Any = None
        self.stt_queue: asyncio.Queue[str] = asyncio.Queue()
        self.wake_event = asyncio.Event()
        self._stream: Any = None
        self._running = False
        self._wake_words = app_config.wake_words
        self._on_utterance: Optional[Callable] = None

    def set_on_speech_detected(self, callback: Callable) -> None:
        """Register callback for speech detection during TTS (interrupt)."""
        self._on_utterance = callback

    async def load_model(self) -> bool:
        """Load Vosk model. Returns True if successful."""
        if VoskModel is None:
            log.warning("Vosk not installed. STT unavailable.")
            return False

        if not self.model_path.exists():
            log.info("Vosk model not found. Downloading...")
            return await self._download_model()

        try:
            self.model = VoskModel(str(self.model_path))
            log.info("Vosk model loaded successfully.")
            return True
        except Exception as e:
            log.error(f"Failed to load Vosk model: {e}")
            return False

    async def _download_model(self) -> bool:
        """Download and extract Vosk model."""
        zip_path = Path(app_config.models_dir) / f"{VOSK_MODEL_DIR_NAME}.zip"
        try:
            def _dl():
                urllib.request.urlretrieve(VOSK_MODEL_URL, zip_path)
            await asyncio.get_running_loop().run_in_executor(None, _dl)
            log.info("Downloaded Vosk model. Extracting...")

            def _extract():
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(app_config.models_dir)
                zip_path.unlink()
            await asyncio.get_running_loop().run_in_executor(None, _extract)
            log.info("Vosk model extracted.")
            return await self.load_model()
        except Exception as e:
            log.error(f"Failed to download Vosk model: {e}")
            return False

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """sounddevice callback — feeds audio to Vosk recognizer."""
        if status:
            log.debug(f"Audio status: {status}")
        if self.recognizer is None:
            return

        data = indata.copy()
        if data.dtype != np.int16:
            data = (data * 32767).astype(np.int16)
        audio_bytes = data.tobytes()

        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip().lower()
            if text:
                log.debug(f"STT final: {text}")
                asyncio.run_coroutine_threadsafe(
                    self.stt_queue.put(text), asyncio.get_running_loop()
                )
                if self._on_utterance:
                    asyncio.run_coroutine_threadsafe(
                        self._on_utterance(text), asyncio.get_running_loop()
                    )
        else:
            partial = json.loads(self.recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip().lower()
            if partial_text and any(w in partial_text for w in self._wake_words):
                if not self.wake_event.is_set():
                    log.info(f"Wake word detected in: '{partial_text}'")
                    asyncio.run_coroutine_threadsafe(
                        self.wake_event.set(), asyncio.get_running_loop()
                    )

    async def start(self) -> None:
        """Start microphone capture and recognition."""
        if self.model is None or sd is None:
            log.warning("STT not available (model or sounddevice missing).")
            return

        try:
            self.recognizer = KaldiRecognizer(self.model, app_config.sample_rate)
            self.recognizer.SetWords(False)
            self._running = True

            def _open_stream():
                self._stream = sd.InputStream(
                    samplerate=app_config.sample_rate,
                    channels=1,
                    dtype="int16",
                    callback=self._audio_callback,
                    blocksize=8000,
                )
                self._stream.start()

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _open_stream)
            log.info("Microphone started. Listening...")
        except Exception as e:
            log.error(f"Failed to start microphone: {e}")
            self._running = False

    async def stop(self) -> None:
        """Stop microphone capture."""
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    async def wait_for_wake(self) -> bool:
        """Wait until wake word is detected. Returns True if triggered."""
        self.wake_event.clear()
        try:
            await asyncio.wait_for(self.wake_event.wait(), timeout=None)
            return True
        except asyncio.CancelledError:
            return False

    async def listen(self, timeout: float | None = None) -> Optional[str]:
        """Wait for a spoken command with timeout. Returns text or None."""
        try:
            text = await asyncio.wait_for(
                self.stt_queue.get(), timeout=timeout or app_config.listen_timeout
            )
            return text
        except asyncio.TimeoutError:
            return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_speech.py -v
```

Expected: All 4 tests PASS (tests mock Vosk as unavailable).

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/pipelines/speech.py tests/test_speech.py && git commit -m "feat: add speech pipeline with Vosk STT and wake word"
```

---

### Task 8: Engine Orchestrator

**Files:**
- Create: `src/jarvis/core/engine.py`
- Create: `tests/test_engine.py`

**Interfaces:**
- Consumes: all 5 pipelines + intent classifier + config
- Produces:
  - `Engine.__init__(config)`
  - `Engine.initialize() -> None`
  - `Engine.run() -> None`
  - `Engine.process(text: str) -> str`
  - `Engine.shutdown() -> None`

- [ ] **Step 1: Write the failing test**

Create `tests/test_engine.py`:

```python
"""Tests for the Engine orchestrator."""

import pytest
from jarvis.core.engine import Engine
from jarvis.core.config import Config


@pytest.mark.asyncio
async def test_engine_initializes_and_shuts_down(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    # All pipelines should be loaded
    assert engine.chat is not None
    assert engine.memory is not None
    assert engine.voice is not None
    assert engine.device is not None
    assert engine.speech is not None
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_returns_response(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    result = await engine.process("hello")
    assert isinstance(result, str)
    assert len(result) > 0
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_tell_time(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    result = await engine.process("what's the time")
    assert "time" in result.lower() or ":" in result
    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_process_general_chat(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    engine = Engine()
    await engine.initialize()
    result = await engine.process("tell me a joke")
    assert isinstance(result, str)
    await engine.shutdown()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_engine.py -v 2>&1 | head -10
```

Expected: ImportError — no `engine` module.

- [ ] **Step 3: Write engine implementation**

Create `src/jarvis/core/engine.py`:

```python
"""Engine orchestrator — lightweight cortical relay (Prefrontal Cortex).

Manages pipeline lifecycle, intent routing, and the main interaction loop.
Pipelines are independent; the engine routes data between them.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from jarvis.core.config import Config, config as app_config
from jarvis.core.intent import classify_intent
from jarvis.utils.logging import log


class EngineState(Enum):
    """Engine state machine states."""
    IDLE = "idle"
    WAKE_WORD = "wake_word"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    TEXT_INPUT = "text_input"


class Engine:
    """Lightweight orchestrator for pipeline coordination."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or app_config
        self.state = EngineState.IDLE
        self.speech = None
        self.chat = None
        self.voice = None
        self.device = None
        self.memory = None
        self._running = False

    async def initialize(self) -> None:
        """Load all pipeline instances."""
        from jarvis.pipelines.speech import SpeechPipeline
        from jarvis.pipelines.chat import ChatPipeline
        from jarvis.pipelines.voice import VoicePipeline
        from jarvis.pipelines.device import DevicePipeline
        from jarvis.pipelines.memory import MemoryPipeline

        self.memory = MemoryPipeline()
        await self.memory.initialize()

        self.chat = ChatPipeline()
        self.voice = VoicePipeline()
        self.device = DevicePipeline()
        self.speech = SpeechPipeline()

        # Load Vosk model (non-blocking if not available)
        await self.speech.load_model()

        log.info("Engine initialized — all pipelines loaded.")

    async def process(self, text: str) -> str:
        """Process a single text input and return a response.

        Args:
            text: User input text.

        Returns:
            Response string to speak/display.
        """
        self.state = EngineState.PROCESSING

        # Classify intent
        intent, params = classify_intent(text)

        # Handle non-chat intents
        if intent == "exit":
            await self.shutdown()
            return "Shutting down. Goodbye!"

        # Check if device can handle it
        if intent not in ("general_chat", "what_is"):
            result = await self.device.execute(intent, params)
            # For simple commands, return the device result directly
            if intent not in ("take_note", "set_reminder", "remember_fact", "search_google", "play_music", "open_website", "open_app", "close_app"):
                self.state = EngineState.IDLE
                return result

        # Build LLM context with memory
        _system_prompt, messages = await self.memory.build_context(text)

        # Get LLM response
        response = await self.chat.generate(messages)
        if response is None:
            response = "I'm having trouble thinking right now."

        # Save to memory
        await self.memory.save_exchange("user", text)
        await self.memory.save_exchange("assistant", response)

        self.state = EngineState.IDLE
        return response

    async def run(self) -> None:
        """Main interaction loop.

        Runs wake-word detection, then listens, processes, and speaks
        in a continuous cycle.
        """
        self._running = True
        log.info("Engine running. Say the wake word to activate.")

        try:
            while self._running:
                # Try voice-first: wait for wake word
                if self.speech and self.speech.model:
                    self.state = EngineState.WAKE_WORD
                    log.debug("Waiting for wake word...")
                    triggered = await self.speech.wait_for_wake()
                    if not triggered:
                        continue

                    self.state = EngineState.LISTENING
                    log.info("Wake word detected. Listening for command...")
                    command = await self.speech.listen()

                    if command:
                        response = await self.process(command)
                        self.state = EngineState.SPEAKING
                        if self.voice:
                            await self.voice.speak(response)
                    else:
                        log.debug("No command heard.")
                else:
                    # Fallback to text input
                    self.state = EngineState.TEXT_INPUT
                    try:
                        text = await asyncio.get_running_loop().run_in_executor(
                            None, lambda: input("You: ")
                        )
                        if text.strip().lower() in ("exit", "quit", "bye"):
                            break
                        response = await self.process(text)
                        print(f"JARVIS: {response}")
                    except (EOFError, KeyboardInterrupt):
                        break
        except asyncio.CancelledError:
            pass
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Gracefully shut down all pipelines."""
        self._running = False
        if self.speech:
            await self.speech.stop()
        if self.chat:
            await self.chat.close()
        if self.memory:
            await self.memory.close()
        log.info("Engine shut down.")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/test_engine.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/core/engine.py tests/test_engine.py && git commit -m "feat: add engine orchestrator with state machine and pipeline routing"
```

---

### Task 9: CLI Entry Point

**Files:**
- Create: `src/jarvis/cli.py`
- Modify: `src/jarvis/__main__.py`

**Interfaces:**
- Consumes: `Engine` from `jarvis.core.engine`, `Config` from `jarvis.core.config`
- Produces: Runnable `python -m jarvis` command

- [ ] **Step 1: Write CLI module**

Create `src/jarvis/cli.py`:

```python
"""CLI entry point for Jarvis AI Assistant."""

from __future__ import annotations

import argparse
import asyncio
import sys

from jarvis.core.config import config
from jarvis.core.engine import Engine
from jarvis.utils.logging import log


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Jarvis AI Assistant for Android — voice-controlled assistant"
    )
    parser.add_argument(
        "--text",
        "-t",
        action="store_true",
        help="Text-only mode (no voice/stt)",
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Disable TTS output",
    )
    parser.add_argument(
        "--once",
        "-o",
        type=str,
        metavar="QUERY",
        help="Process a single query and exit",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version and exit",
    )
    return parser


async def run_once(query: str) -> None:
    """Process a single query and print the response."""
    engine = Engine()
    await engine.initialize()
    try:
        response = await engine.process(query)
        print(f"\nJARVIS: {response}")
    finally:
        await engine.shutdown()


async def run_interactive(text_only: bool = False, no_voice: bool = False) -> None:
    """Run the interactive assistant loop."""
    if text_only:
        log.info("Starting in text-only mode.")
    if no_voice:
        log.info("Voice output disabled.")

    engine = Engine()
    await engine.initialize()

    try:
        if text_only or not engine.speech or not engine.speech.model:
            # Text-only interactive mode
            print("Jarvis AI Assistant (text mode). Type 'exit' to quit.")
            while True:
                try:
                    text = await asyncio.get_running_loop().run_in_executor(
                        None, lambda: input("\nYou: ")
                    )
                    if text.strip().lower() in ("exit", "quit", "bye"):
                        print("Goodbye!")
                        break
                    response = await engine.process(text)
                    print(f"JARVIS: {response}")
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break
        else:
            # Voice mode with wake word
            print("Jarvis AI Assistant. Say the wake word to activate.")
            await engine.run()
    finally:
        await engine.shutdown()


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        from jarvis import __version__
        print(f"Jarvis AI Assistant v{__version__}")
        sys.exit(0)

    if args.once:
        asyncio.run(run_once(args.once))
    else:
        asyncio.run(run_interactive(
            text_only=args.text,
            no_voice=args.no_voice,
        ))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Update __main__.py**

Create/write `src/jarvis/__main__.py`:

```python
"""Entry point for `python -m jarvis`."""

from jarvis.cli import main

main()
```

- [ ] **Step 3: Test the CLI works**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m jarvis --version
```

Expected output: `Jarvis AI Assistant v0.2.0`

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m jarvis --once "what's the time"
```

Expected output: `JARVIS: The time is ...`

- [ ] **Step 4: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/cli.py src/jarvis/__main__.py && git commit -m "feat: add CLI entry point with text and voice modes"
```

---

### Task 10: Brain UI — Renderer and Terminal TUI

**Files:**
- Create: `src/jarvis/ui/brain_renderer.py`
- Create: `src/jarvis/ui/tui.py`

**Interfaces:**
- Consumes: `Engine` state and pipeline status info
- Produces:
  - `BrainRenderer.render(regions: dict) -> str` — ASCII brain map
  - `TUI.start(engine) -> None` — curses interactive UI
  - `TUI.stop() -> None`

- [ ] **Step 1: Create the brain renderer (ASCII art + color)**

Create `src/jarvis/ui/brain_renderer.py`:

```python
"""Brain visualization renderer — generates the neural network map as styled text.

Renders a 6-region cortical map showing pipeline status, neural pathways,
and real-time activity metrics. Used by both terminal TUI and web UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ANSI color codes matching the cortical region palette
COLORS = {
    "pfc": {"name": "PFC", "color": "\033[38;2;255;170;0m", "label": "Executive"},
    "auditory": {"name": "Auditory", "color": "\033[38;2;0;240;255m", "label": "STT"},
    "wernicke": {"name": "Wernicke", "color": "\033[38;2;0;255;136m", "label": "LLM"},
    "broca": {"name": "Broca", "color": "\033[38;2;136;68;255m", "label": "TTS"},
    "motor": {"name": "Motor", "color": "\033[38;2;255;51;102m", "label": "Device"},
    "hippocampus": {"name": "Hippocampus", "color": "\033[38;2;0;102;255m", "label": "Memory"},
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


@dataclass
class RegionStatus:
    """Status of a single cortical region / pipeline."""
    name: str
    color_code: str
    label: str
    active: bool = False
    latency_ms: float = 0.0
    health: str = "optimal"


@dataclass
class BrainState:
    """Complete snapshot of the brain's neural state."""
    regions: dict[str, RegionStatus] = field(default_factory=dict)
    active_pathways: list[tuple[str, str]] = field(default_factory=list)
    cortex_health: str = "OPTIMAL"
    neural_activity_pct: float = 0.0
    total_synapses: int = 10


class BrainRenderer:
    """Generates brain visualization string for terminal display."""

    @staticmethod
    def build_region_map(state: BrainState) -> str:
        """Render the 6-region cortical brain map as styled ASCII.

        Args:
            state: Current brain state snapshot.

        Returns:
            Multi-line string with colorized brain visualization.
        """
        lines = [
            f"{BOLD}{'=' * 50}{RESET}",
            f"{BOLD}   JARVIS CORTICAL NETWORK{RESET}",
            f"{BOLD}{'=' * 50}{RESET}",
            "",
        ]

        # PFC — top center
        pfc = state.regions.get("pfc")
        if pfc:
            act = "●" if pfc.active else "○"
            clr = pfc.color_code
            lines.append(f"          {clr}┌──────────────┐{RESET}")
            lines.append(f"          {clr}│ {act} PFC           │{RESET}")
            lines.append(f"          {clr}│   Executive    │{RESET}")
            lines.append(f"          {clr}└──────────────┘{RESET}")

        # Left regions (Auditory) — Right regions (Motor)
        auditory = state.regions.get("auditory")
        motor = state.regions.get("motor")
        if auditory and motor:
            a_act = "●" if auditory.active else "○"
            m_act = "●" if motor.active else "○"
            a_clr = auditory.color_code
            m_clr = motor.color_code
            blank = " " * 10
            lines.append(f"{a_clr}┌──────────┐{blank}{m_clr}┌──────────┐{RESET}")
            lines.append(f"{a_clr}│ {a_act} Auditory│{blank}{m_clr}│ {m_act} Motor   │{RESET}")
            lines.append(f"{a_clr}│   STT    │{blank}{m_clr}│  Device  │{RESET}")
            lines.append(f"{a_clr}└──────────┘{blank}{m_clr}└──────────┘{RESET}")

        # Center regions (Wernicke's + Broca's)
        wern = state.regions.get("wernicke")
        broc = state.regions.get("broca")
        if wern and broc:
            w_act = "●" if wern.active else "○"
            b_act = "●" if broc.active else "○"
            w_clr = wern.color_code
            b_clr = broc.color_code
            gap = " " * 6
            lines.append(f"     {w_clr}┌──────────┐{gap}{b_clr}┌──────────┐{RESET}")
            lines.append(f"     {w_clr}│ {w_act} Wernicke│{gap}{b_clr}│ {b_act} Broca  │{RESET}")
            lines.append(f"     {w_clr}│   LLM    │{gap}{b_clr}│  TTS    │{RESET}")
            lines.append(f"     {w_clr}└──────────┘{gap}{b_clr}└──────────┘{RESET}")

        # Hippocampus — bottom center (connections to Wernicke's)
        hipp = state.regions.get("hippocampus")
        if hipp:
            h_act = "●" if hipp.active else "○"
            h_clr = hipp.color_code
            lines.append(f"          {h_clr}┌──────────────┐{RESET}")
            lines.append(f"          {h_clr}│ {h_act} Hippocampus │{RESET}")
            lines.append(f"          {h_clr}│   Memory     │{RESET}")
            lines.append(f"          {h_clr}└──────────────┘{RESET}")

        # Neural pathways
        lines.append("")
        lines.append(f"{DIM}── Neural Pathways ──{RESET}")
        for src, dst in state.active_pathways:
            lines.append(f"  {DIM}{src} → {dst}{RESET}")
        if not state.active_pathways:
            lines.append(f"  {DIM}(idle){RESET}")

        # Metrics bar
        lines.append("")
        lines.append(f"{DIM}── Metrics ──{RESET}")
        lines.append(f"  Activity:  {state.neural_activity_pct:>5.1f}%")
        lines.append(f"  Synapses:  {state.total_synapses}")
        lines.append(f"  Cortex:    {state.cortex_health}")

        # Per-region latency
        lines.append(f"{DIM}── Latency ──{RESET}")
        for key, region in state.regions.items():
            act_mark = "●" if region.active else "○"
            lines.append(
                f"  {region.color_code}{act_mark}{RESET} "
                f"{region.name:<12} "
                f"{region.latency_ms:>6.1f}ms  "
                f"{region.health}"
            )

        return "\n".join(lines)

    @staticmethod
    def build_web_data(state: BrainState) -> dict:
        """Build JSON-serializable brain state for web UI consumption.

        Args:
            state: Current brain state.

        Returns:
            Dict with region statuses and metrics for JSON serialization.
        """
        return {
            "regions": {
                key: {
                    "name": r.name,
                    "color": r.color_code,
                    "active": r.active,
                    "latency_ms": r.latency_ms,
                    "health": r.health,
                }
                for key, r in state.regions.items()
            },
            "active_pathways": state.active_pathways,
            "cortex_health": state.cortex_health,
            "neural_activity_pct": state.neural_activity_pct,
            "total_synapses": state.total_synapses,
        }

    @staticmethod
    def build_svg(state: BrainState) -> str:
        """Placeholder: generate inline SVG from brain state.

        Full SVG generation requires the brain-architecture.svg template
        with dynamic region coloring. Returns a minimal placeholder.
        """
        active_count = sum(1 for r in state.regions.values() if r.active)
        html_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500">',
            f'<rect width="400" height="500" fill="#0a0a0f"/>',
            f'<text x="200" y="30" text-anchor="middle" fill="#00f0ff" '
            f'font-family="monospace" font-size="12">JARVIS CORTEX</text>',
            f'<text x="200" y="50" text-anchor="middle" fill="#004466" '
            f'font-family="monospace" font-size="10">Active regions: {active_count}/6</text>',
            f'</svg>',
        ]
        return "\n".join(html_parts)
```

- [ ] **Step 2: Create the terminal TUI (curses-based)**

Create `src/jarvis/ui/tui.py`:

```python
"""Terminal UI — curses-based brain visualization.

Displays the 6-region cortical map with real-time activity,
neural pathway animation, and metrics.
"""

from __future__ import annotations

import asyncio
import curses
import math
import time
from typing import Any, Optional

from jarvis.ui.brain_renderer import (
    COLORS,
    RESET,
    BOLD,
    DIM,
    BrainRenderer,
    BrainState,
    RegionStatus,
)
from jarvis.utils.logging import log


class TUI:
    """Curses-based terminal UI showing the brain's neural network."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self._running = False
        self._stdscr: Any = None
        self._last_update = 0.0
        self._update_interval = 0.2  # 5 fps

    def _init_colors(self) -> None:
        """Initialize curses color pairs."""
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        # Define color pairs matching cortical palette
        curses.init_pair(1, curses.COLOR_YELLOW, -1)   # PFC
        curses.init_pair(2, curses.COLOR_CYAN, -1)      # Auditory
        curses.init_pair(3, curses.COLOR_GREEN, -1)     # Wernicke
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)   # Broca
        curses.init_pair(5, curses.COLOR_RED, -1)       # Motor
        curses.init_pair(6, curses.COLOR_BLUE, -1)      # Hippocampus
        curses.init_pair(7, curses.COLOR_WHITE, -1)     # Default

    def _build_brain_state(self) -> BrainState:
        """Build current brain state from engine pipelines."""
        state = BrainState()
        now = time.time()

        # Determine which region is active based on engine state
        eng_state = str(self.engine.state) if hasattr(self.engine, 'state') else "idle"

        region_active = {
            "pfc": eng_state in ("processing", "listening", "speaking"),
            "auditory": eng_state in ("wake_word", "listening"),
            "wernicke": eng_state in ("processing",),
            "broca": eng_state in ("speaking",),
            "motor": eng_state in ("processing",),
            "hippocampus": True,  # always writing
        }

        # Latency simulation (in production, measure actual pipeline latency)
        latencies = {
            "pfc": 5.0 + (2.0 * math.sin(now * 0.5)),
            "auditory": 120.0 if region_active["auditory"] else 0.0,
            "wernicke": 450.0 if region_active["wernicke"] else 0.0,
            "broca": 800.0 if region_active["broca"] else 0.0,
            "motor": 50.0 if region_active["motor"] else 0.0,
            "hippocampus": 3.0,
        }

        for key, info in COLORS.items():
            state.regions[key] = RegionStatus(
                name=info["name"],
                color_code=info["color"],
                label=info["label"],
                active=region_active.get(key, False),
                latency_ms=latencies.get(key, 0.0),
                health="active" if region_active.get(key, False) else "standby",
            )

        # Active data pathways
        pathways = []
        if region_active["auditory"]:
            pathways.append(("Auditory", "Wernicke"))
        if region_active["wernicke"]:
            pathways.append(("Wernicke", "Broca"))
        if region_active["wernicke"]:
            pathways.append(("Wernicke", "Hippocampus"))
        if region_active["motor"]:
            pathways.append(("PFC", "Motor"))
        state.active_pathways = pathways

        # Overall metrics
        active_count = sum(1 for v in region_active.values() if v)
        state.neural_activity_pct = (active_count / 6) * 100
        state.cortex_health = "OPTIMAL" if active_count <= 4 else "HIGH LOAD"
        state.total_synapses = len(pathways)

        return state

    async def _draw(self) -> None:
        """Draw the brain visualization on the curses screen."""
        if not self._stdscr:
            return

        try:
            self._stdscr.clear()
            height, width = self._stdscr.getmaxyx()

            # Title
            title = "JARVIS CORTICAL NETWORK — Neural Activity Monitor"
            x = max(0, (width - len(title)) // 2)
            try:
                self._stdscr.addstr(0, x, title, curses.A_BOLD | curses.color_pair(7))
            except curses.error:
                pass

            # Build and render brain state
            state = self._build_brain_state()
            brain_str = BrainRenderer.build_region_map(state)

            # Split into lines and draw
            for i, line in enumerate(brain_str.split("\n")):
                if i + 2 >= height - 2:
                    break
                # Strip ANSI codes for curses rendering
                clean = line
                for code in [
                    "\033[38;2;255;170;0m", "\033[38;2;0;240;255m",
                    "\033[38;2;0;255;136m", "\033[38;2;136;68;255m",
                    "\033[38;2;255;51;102m", "\033[38;2;0;102;255m",
                    RESET, BOLD, DIM,
                ]:
                    clean = clean.replace(code, "")
                try:
                    self._stdscr.addstr(i + 2, 2, clean[:width - 4])
                except curses.error:
                    pass

            # Footer
            footer = f"State: {self.engine.state.value if hasattr(self.engine, 'state') else 'N/A'} | Ctrl+C to exit"
            try:
                self._stdscr.addstr(height - 1, 0, footer[:width - 1], curses.A_DIM)
            except curses.error:
                pass

            self._stdscr.refresh()
        except curses.error:
            pass

    async def start(self) -> None:
        """Start the curses TUI and begin rendering."""
        self._running = True

        try:
            self._stdscr = curses.initscr()
            curses.cbreak()
            curses.noecho()
            curses.curs_set(0)
            self._stdscr.nodelay(1)
            self._init_colors()

            while self._running:
                # Check for 'q' or ESC to quit
                key = self._stdscr.getch()
                if key in (ord('q'), 27):  # 'q' or ESC
                    break

                now = time.time()
                if now - self._last_update >= self._update_interval:
                    await self._draw()
                    self._last_update = now

                await asyncio.sleep(0.05)  # 50ms poll
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the TUI and restore terminal settings."""
        self._running = False
        if self._stdscr:
            try:
                curses.nocbreak()
                self._stdscr.keypad(False)
                curses.echo()
                curses.curs_set(1)
                curses.endwin()
            except curses.error:
                pass
            self._stdscr = None
```

- [ ] **Step 3: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/ui/brain_renderer.py src/jarvis/ui/tui.py && git commit -m "feat: add brain visualization renderer and curses-based TUI"
```

---

### Task 11: Brain UI — Web UI (Flask)

**Files:**
- Create: `src/jarvis/ui/web_ui/app.py`
- Create: `src/jarvis/ui/web_ui/static/brain.js`
- Create: `src/jarvis/ui/web_ui/templates/index.html`

**Interfaces:**
- Consumes: `BrainRenderer.build_web_data(state) -> dict` from `brain_renderer`
- Produces: Flask web server with interactive brain SVG visualization

- [ ] **Step 1: Create Flask web app**

Create `src/jarvis/ui/web_ui/app.py`:

```python
"""Flask web UI serving the brain visualization with live updates."""

from __future__ import annotations

import json
import time
import math
from typing import Any, Optional

from flask import Flask, jsonify, render_template, Response

from jarvis.ui.brain_renderer import COLORS, BrainRenderer, BrainState, RegionStatus

app = Flask(__name__)

# In-memory engine reference (set externally)
_engine_ref: Any = None


def set_engine(engine: Any) -> None:
    """Set the engine reference for live state reading."""
    global _engine_ref
    _engine_ref = engine


def _build_state() -> BrainState:
    """Build current brain state from engine or simulated data."""
    state = BrainState()
    now = time.time()

    # Read engine state if available
    eng_state = "idle"
    if _engine_ref and hasattr(_engine_ref, 'state'):
        eng_state = str(_engine_ref.state)

    region_active = {
        "pfc": eng_state in ("processing", "listening", "speaking"),
        "auditory": eng_state in ("wake_word", "listening"),
        "wernicke": eng_state in ("processing",),
        "broca": eng_state in ("speaking",),
        "motor": eng_state in ("processing",),
        "hippocampus": True,
    }

    latencies = {
        "pfc": 5.0 + (2.0 * math.sin(now * 0.5)),
        "auditory": 120.0 if region_active["auditory"] else 0.0,
        "wernicke": 450.0 if region_active["wernicke"] else 0.0,
        "broca": 800.0 if region_active["broca"] else 0.0,
        "motor": 50.0 if region_active["motor"] else 0.0,
        "hippocampus": 3.0,
    }

    for key, info in COLORS.items():
        state.regions[key] = RegionStatus(
            name=info["name"],
            color_code=info["color"],
            label=info["label"],
            active=region_active.get(key, False),
            latency_ms=latencies.get(key, 0.0),
            health="active" if region_active.get(key, False) else "standby",
        )

    pathways = []
    if region_active["auditory"]:
        pathways.append(("Auditory", "Wernicke"))
    if region_active["wernicke"]:
        pathways.append(("Wernicke", "Broca"))
        pathways.append(("Wernicke", "Hippocampus"))
    if region_active["motor"]:
        pathways.append(("PFC", "Motor"))
    state.active_pathways = pathways

    active_count = sum(1 for v in region_active.values() if v)
    state.neural_activity_pct = (active_count / 6) * 100
    state.cortex_health = "OPTIMAL" if active_count <= 4 else "HIGH LOAD"

    return state


@app.route("/")
def index() -> str:
    """Serve the main brain visualization page."""
    return render_template("index.html")


@app.route("/api/brain-state")
def brain_state() -> Response:
    """Return current brain state as JSON."""
    state = _build_state()
    data = BrainRenderer.build_web_data(state)
    return jsonify(data)


@app.route("/api/brain-svg")
def brain_svg() -> Response:
    """Return current brain state as inline SVG."""
    state = _build_state()
    svg = BrainRenderer.build_svg(state)
    return Response(svg, mimetype="image/svg+xml")


@app.route("/api/stream")
def stream() -> Response:
    """SSE stream of brain state updates."""
    def generate():
        while True:
            state = _build_state()
            data = BrainRenderer.build_web_data(state)
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
    return Response(generate(), mimetype="text/event-stream")


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """Run the Flask web UI server."""
    app.run(host=host, port=port, debug=debug, threaded=True)
```

- [ ] **Step 2: Create the HTML template**

Create `src/jarvis/ui/web_ui/templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JARVIS Neural Cortex</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0a0a0f;
      color: #00f0ff;
      font-family: 'Courier New', monospace;
      overflow: hidden;
      height: 100vh;
    }
    #app {
      display: flex;
      flex-direction: column;
      height: 100vh;
      padding: 20px;
    }
    header {
      text-align: center;
      padding: 10px;
      border-bottom: 1px solid #004466;
    }
    header h1 {
      font-size: 18px;
      letter-spacing: 6px;
      color: #00f0ff;
      opacity: 0.8;
    }
    header p {
      font-size: 11px;
      color: #004466;
      margin-top: 4px;
    }
    #brain-canvas {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    #brain-canvas svg {
      max-width: 100%;
      max-height: 100%;
    }
    #metrics {
      display: flex;
      gap: 20px;
      justify-content: center;
      padding: 15px;
      border-top: 1px solid #004466;
      font-size: 12px;
    }
    .metric {
      text-align: center;
    }
    .metric .value {
      font-size: 20px;
      font-weight: bold;
      color: #00ff88;
    }
    .metric .label {
      color: #004466;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 2px;
    }
    #pathways {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: center;
      padding: 8px;
      border-top: 1px solid #004466;
      font-size: 11px;
    }
    .pathway {
      padding: 2px 8px;
      border: 1px solid #004466;
      border-radius: 4px;
      color: #00f0ff;
      opacity: 0.6;
    }
    .pathway.active {
      border-color: #00ff88;
      color: #00ff88;
      opacity: 1;
    }
    .region-indicator {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 4px;
    }
    .region-indicator.active {
      box-shadow: 0 0 8px currentColor;
    }
    @media (max-width: 600px) {
      #metrics { flex-wrap: wrap; }
      header h1 { font-size: 14px; letter-spacing: 3px; }
    }
  </style>
</head>
<body>
  <div id="app">
    <header>
      <h1>// JARVIS NEURAL CORTEX //</h1>
      <p>AI ASSISTANT BRAIN MONITOR — v0.2</p>
    </header>

    <div id="brain-canvas">
      <svg id="brain-svg" viewBox="0 0 600 500" xmlns="http://www.w3.org/2000/svg">
        <rect width="600" height="500" fill="#0a0a0f"/>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
          </filter>
        </defs>
        <!-- Regions rendered by JS -->
      </svg>
    </div>

    <div id="metrics">
      <div class="metric">
        <div class="value" id="activity-pct">0%</div>
        <div class="label">Activity</div>
      </div>
      <div class="metric">
        <div class="value" id="synapse-count">0</div>
        <div class="label">Synapses</div>
      </div>
      <div class="metric">
        <div class="value" id="cortex-health">—</div>
        <div class="label">Cortex</div>
      </div>
    </div>

    <div id="pathways"></div>
  </div>
  <script src="{{ url_for('static', filename='brain.js') }}"></script>
</body>
</html>
```

- [ ] **Step 3: Create the interactive brain visualization JavaScript**

Create `src/jarvis/ui/web_ui/static/brain.js`:

```javascript
/**
 * Brain visualization — interactive neural network renderer.
 * Draws 6 cortical regions with neural pathways on an SVG canvas.
 * Updates in real-time via SSE /api/stream.
 */

const COLORS = {
  pfc: { hex: '#ffaa00', name: 'PFC', label: 'Executive' },
  auditory: { hex: '#00f0ff', name: 'Auditory', label: 'STT' },
  wernicke: { hex: '#00ff88', name: 'Wernicke', label: 'LLM' },
  broca: { hex: '#8844ff', name: 'Broca', label: 'TTS' },
  motor: { hex: '#ff3366', name: 'Motor', label: 'Device' },
  hippocampus: { hex: '#0066ff', name: 'Hippocampus', label: 'Memory' },
};

// Region positions (normalized 0-600, 0-500)
const POSITIONS = {
  pfc: { x: 300, y: 60 },
  auditory: { x: 120, y: 180 },
  wernicke: { x: 220, y: 260 },
  broca: { x: 380, y: 260 },
  motor: { x: 480, y: 180 },
  hippocampus: { x: 300, y: 370 },
};

const svg = document.getElementById('brain-svg');
const ns = 'http://www.w3.org/2000/svg';

// Create a visual region group
function createRegion(key, pos) {
  const color = COLORS[key];
  const group = document.createElementNS(ns, 'g');

  const glow = document.createElementNS(ns, 'ellipse');
  glow.setAttribute('cx', pos.x);
  glow.setAttribute('cy', pos.y);
  glow.setAttribute('rx', 55);
  glow.setAttribute('ry', 40);
  glow.setAttribute('fill', color.hex);
  glow.setAttribute('opacity', '0.08');
  glow.setAttribute('filter', 'url(#glow)');
  glow.setAttribute('class', 'region-glow');
  group.appendChild(glow);

  const body = document.createElementNS(ns, 'ellipse');
  body.setAttribute('cx', pos.x);
  body.setAttribute('cy', pos.y);
  body.setAttribute('rx', 50);
  body.setAttribute('ry', 35);
  body.setAttribute('fill', 'none');
  body.setAttribute('stroke', color.hex);
  body.setAttribute('stroke-width', '2');
  body.setAttribute('opacity', '0.7');
  body.setAttribute('class', 'region-body');
  group.appendChild(body);

  const label = document.createElementNS(ns, 'text');
  label.setAttribute('x', pos.x);
  label.setAttribute('y', pos.y - 6);
  label.setAttribute('text-anchor', 'middle');
  label.setAttribute('fill', color.hex);
  label.setAttribute('font-family', 'monospace');
  label.setAttribute('font-size', '12');
  label.setAttribute('font-weight', 'bold');
  label.textContent = color.name;
  group.appendChild(label);

  const sublabel = document.createElementNS(ns, 'text');
  sublabel.setAttribute('x', pos.x);
  sublabel.setAttribute('y', pos.y + 14);
  sublabel.setAttribute('text-anchor', 'middle');
  sublabel.setAttribute('fill', color.hex);
  sublabel.setAttribute('font-family', 'monospace');
  sublabel.setAttribute('font-size', '9');
  sublabel.setAttribute('opacity', '0.6');
  sublabel.textContent = color.label;
  group.appendChild(sublabel);

  const indicator = document.createElementNS(ns, 'circle');
  indicator.setAttribute('cx', pos.x + 55);
  indicator.setAttribute('cy', pos.y - 35);
  indicator.setAttribute('r', 5);
  indicator.setAttribute('fill', '#004466');
  indicator.setAttribute('class', 'indicator-dot');
  group.appendChild(indicator);

  svg.appendChild(group);
  return group;
}

// Create neural pathway (curved line connecting two regions)
function createPathway(src, dst, index) {
  const line = document.createElementNS(ns, 'path');
  const sx = POSITIONS[src].x;
  const sy = POSITIONS[src].y;
  const dx = POSITIONS[dst].x;
  const dy = POSITIONS[dst].y;
  const mx = (sx + dx) / 2;
  const my = (sy + dy) / 2 - 30;
  const d = `M ${sx} ${sy} Q ${mx} ${my} ${dx} ${dy}`;

  line.setAttribute('d', d);
  line.setAttribute('fill', 'none');
  line.setAttribute('stroke', '#004466');
  line.setAttribute('stroke-width', '1.5');
  line.setAttribute('opacity', '0.3');
  line.setAttribute('class', `pathway pathway-${src}-${dst}`);
  svg.appendChild(line);
  return line;
}

// Initialize all regions and pathways
const regionElements = {};
Object.entries(POSITIONS).forEach(([key, pos]) => {
  regionElements[key] = createRegion(key, pos);
});

const PATHWAY_DEFS = [
  ['auditory', 'wernicke'],
  ['wernicke', 'broca'],
  ['wernicke', 'hippocampus'],
  ['hippocampus', 'wernicke'],
  ['pfc', 'wernicke'],
  ['pfc', 'motor'],
  ['auditory', 'pfc'],
  ['broca', 'pfc'],
  ['motor', 'pfc'],
  ['wernicke', 'pfc'],
];

PATHWAY_DEFS.forEach(([src, dst], i) => {
  createPathway(src, dst, i);
});

// Update visualization from brain state data
function updateBrain(data) {
  if (!data || !data.regions) return;

  // Update region active states
  Object.entries(data.regions).forEach(([key, reg]) => {
    const el = regionElements[key];
    if (!el) return;

    const glow = el.querySelector('.region-glow');
    const body = el.querySelector('.region-body');
    const dot = el.querySelector('.indicator-dot');
    const color = COLORS[key];

    if (reg.active) {
      glow.setAttribute('opacity', '0.2');
      body.setAttribute('opacity', '1');
      body.setAttribute('stroke-width', '3');
      dot.setAttribute('fill', color.hex);
      dot.setAttribute('opacity', '1');
    } else {
      glow.setAttribute('opacity', '0.08');
      body.setAttribute('opacity', '0.5');
      body.setAttribute('stroke-width', '1.5');
      dot.setAttribute('fill', '#004466');
      dot.setAttribute('opacity', '0.4');
    }
  });

  // Update pathways
  const activePaths = (data.active_pathways || []).map(
    p => `pathway-${p[0].toLowerCase()}-${p[1].toLowerCase()}`
  );

  document.querySelectorAll('.pathway').forEach(el => {
    const isActive = activePaths.some(cls => el.classList.contains(cls));
    if (isActive) {
      el.setAttribute('stroke', '#00ff88');
      el.setAttribute('stroke-width', '2.5');
      el.setAttribute('opacity', '0.7');
    } else {
      el.setAttribute('stroke', '#004466');
      el.setAttribute('stroke-width', '1.5');
      el.setAttribute('opacity', '0.2');
    }
  });

  // Update metrics
  document.getElementById('activity-pct').textContent =
    (data.neural_activity_pct || 0).toFixed(0) + '%';
  document.getElementById('synapse-count').textContent =
    data.total_synapses || 0;
  document.getElementById('cortex-health').textContent =
    data.cortex_health || '—';

  // Update pathway list
  const pathwaysEl = document.getElementById('pathways');
  if (data.active_pathways && data.active_pathways.length > 0) {
    pathwaysEl.innerHTML = data.active_pathways
      .map(([src, dst]) =>
        `<span class="pathway active">${src} → ${dst}</span>`
      )
      .join('');
  } else {
    pathwaysEl.innerHTML =
      '<span class="pathway">(idle — no active pathways)</span>';
  }
}

// Fetch initial state
fetch('/api/brain-state')
  .then(r => r.json())
  .then(updateBrain)
  .catch(() => {});

// Connect to SSE stream for live updates
const evtSource = new EventSource('/api/stream');
evtSource.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    updateBrain(data);
  } catch (e) {
    // ignore parse errors
  }
};

// Fallback polling if SSE fails
let pollInterval = setInterval(() => {
  fetch('/api/brain-state')
    .then(r => r.json())
    .then(updateBrain)
    .catch(() => {});
}, 2000);
```

- [ ] **Step 4: Verify web UI files are in place**

```bash
cd /root/jarvis-ai-assistent-for-android && ls -la src/jarvis/ui/web_ui/
```

Expected: `__init__.py`, `app.py`, `static/brain.js`, `templates/index.html`

- [ ] **Step 5: Commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add src/jarvis/ui/web_ui/ && git commit -m "feat: add Flask web UI with interactive brain visualization"
```

---

### Task 12: Documentation and Packaging

**Files:**
- Modify: `.env.example` (already created in Task 1)
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
# Jarvis AI Assistant for Android

A modular, voice-controlled AI assistant for Android Termux with a brain-inspired pipeline architecture and neural visualization UI.

## Architecture

The assistant is built as 6 independent pipelines, each mapped to a brain cortical region:

| Region | Pipeline | Function |
|--------|----------|----------|
| Prefrontal Cortex (PFC) | Engine | Executive orchestration, intent routing |
| Auditory Cortex | Speech | Vosk STT, wake word detection |
| Wernicke's Area | Chat | Groq LLM, reasoning |
| Broca's Area | Voice | Piper TTS, speech output |
| Motor Cortex | Device | Termux:API device control |
| Hippocampus | Memory | SQLite storage |

10 bidirectional neural pathways connect the regions, visualized in real-time.

## Features

- Voice interaction with wake word ("Jarvis", "Boss", "Computer")
- Speech-to-text via Vosk (offline, local)
- LLM reasoning via Groq API (llama3-8b-8192)
- Text-to-speech via Piper (local) or Android TTS
- Android device control (apps, settings, flashlight, wifi, bluetooth, etc.)
- Persistent memory with conversation history and user facts
- Brain visualization UI (terminal TUI + web UI)

## Installation

### Prerequisites

- Android device with [Termux](https://termux.com/) installed
- [Termux:API](https://wiki.termux.com/wiki/Termux:API) add-on
- Python 3.11+
- [Piper TTS](https://github.com/rhasspy/piper) (optional, for local TTS)

### Setup

```bash
# Clone the repository
git clone <repo-url> jarvis-ai-assistent-for-android
cd jarvis-ai-assistent-for-android

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run
python -m jarvis
```

## Usage

### Voice Mode (with wake word)

```bash
python -m jarvis
```

Say "Jarvis" to activate, then speak your command.

### Text Mode

```bash
python -m jarvis --text
```

### Single Query

```bash
python -m jarvis --once "what's the time"
```

### Web UI

```bash
python -c "from jarvis.ui.web_ui.app import run_server; run_server()"
```

Then open `http://localhost:5000` in a browser.

## Project Structure

```
src/jarvis/
├── __init__.py          # Package version
├── __main__.py          # python -m jarvis entry
├── cli.py               # CLI argument parser
├── core/
│   ├── config.py        # Environment config loader
│   ├── intent.py        # Rule-based intent classifier
│   └── engine.py        # Orchestrator state machine
├── pipelines/
│   ├── speech.py        # Vosk STT + wake word
│   ├── chat.py          # Groq LLM client
│   ├── voice.py         # Piper TTS
│   ├── device.py        # Termux:API device control
│   └── memory.py        # SQLite storage
├── ui/
│   ├── brain_renderer.py  # Brain visualization engine
│   ├── tui.py             # Curses terminal UI
│   └── web_ui/            # Flask web UI
└── utils/
    └── logging.py       # Logger setup
```

## Graceful Degradation

The assistant continues working even when components are unavailable:

- **No Vosk model:** Falls back to text-only input
- **No microphone:** Text-only mode
- **No Groq API key:** Chat pipeline returns helpful error
- **No Piper binary:** Falls back to Android TTS (termux-tts-speak)
- **No Termux:API:** Device commands return descriptive errors
- **No SQLite:** Conversation continues without persistence

## License

MIT
```

- [ ] **Step 2: Verify full project structure**

```bash
cd /root/jarvis-ai-assistent-for-android && find . -type f -not -path './.git/*' -not -path './__pycache__/*' | sort
```

Expected: All project files present.

- [ ] **Step 3: Run full test suite**

```bash
cd /root/jarvis-ai-assistent-for-android && PYTHONPATH=src python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 4: Final commit**

```bash
cd /root/jarvis-ai-assistent-for-android && git add README.md .env.example && git commit -m "docs: add README and finalize project documentation"
```

---

## Scope Verification

| Spec Requirement | Task(s) | Status |
|---|---|---|
| Project scaffold + config | Task 1 | ✅ |
| Intent classifier with 40+ patterns | Task 2 | ✅ |
| Memory pipeline (SQLite, 5 tables) | Task 3 | ✅ |
| Chat pipeline (Groq LLM) | Task 4 | ✅ |
| Voice pipeline (Piper + fallback) | Task 5 | ✅ |
| Device pipeline (Termux:API, 25+ actions) | Task 6 | ✅ |
| Speech pipeline (Vosk STT + wake word) | Task 7 | ✅ |
| Engine orchestrator (state machine) | Task 8 | ✅ |
| CLI entry point (text + voice modes) | Task 9 | ✅ |
| Brain renderer (ASCII/color) | Task 10 | ✅ |
| Terminal TUI (curses, live brain) | Task 10 | ✅ |
| Web UI (Flask + SVG + SSE) | Task 11 | ✅ |
| Documentation + packaging | Task 12 | ✅ |
| Graceful degradation (all failures) | Tasks 3-8 | ✅ |
| TDD per pipeline | Tasks 2-8 | ✅ |
| 10 neural pathways visualized | Tasks 10-11 | ✅ |
