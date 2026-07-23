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

