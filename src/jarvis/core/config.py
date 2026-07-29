"""Environment-based configuration loader. Crafted by Minaty001."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]


@dataclass
class Config:
    """Immutable configuration loaded from .env / environment variables."""

    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "llama-3.1-8b-instant"))
    groq_api_base: str = field(default_factory=lambda: os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1"))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    openai_api_base: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    database_path: str = field(default_factory=lambda: os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "jarvis.db")))
    models_dir: str = field(default_factory=lambda: os.getenv("MODELS_DIR", str(BASE_DIR / "models")))
    voices_dir: str = field(default_factory=lambda: os.getenv("VOICES_DIR", str(BASE_DIR / "voices")))
    logs_dir: str = field(default_factory=lambda: os.getenv("LOGS_DIR", str(BASE_DIR / "logs")))
    wake_words: list[str] = field(default_factory=lambda: [w.strip().lower() for w in os.getenv("WAKE_WORDS", "jarvis,boss,computer").split(",") if w.strip()])
    sample_rate: int = field(default_factory=lambda: int(os.getenv("SAMPLE_RATE", "16000")))
    listen_timeout: float = field(default_factory=lambda: float(os.getenv("LISTEN_TIMEOUT", "5.0")))
    groq_timeout: float = field(default_factory=lambda: float(os.getenv("GROQ_TIMEOUT", "30.0")))
    max_history: int = field(default_factory=lambda: int(os.getenv("MAX_HISTORY", "20")))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.7")))
    llm_max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "512")))
    tts_rate: int = field(default_factory=lambda: int(os.getenv("TTS_RATE", "175")))
    tts_pitch: int = field(default_factory=lambda: int(os.getenv("TTS_PITCH", "100")))

    # Runtime environment detections (useful for Termux fallbacks)
    is_termux: bool = field(default_factory=lambda: bool(os.getenv("TERMUX_VERSION") or Path("/data/data/com.termux").exists()))
    termux_api_available: bool = field(default_factory=lambda: shutil.which("termux-microphone-record") is not None and shutil.which("termux-tts-speak") is not None)
    has_piper: bool = field(default_factory=lambda: shutil.which("piper") is not None)
    has_edge_tts: bool = field(default_factory=lambda: shutil.which("paplay") is not None or shutil.which("play") is not None)

    def __post_init__(self) -> None:
        """Ensure required directories exist and log environment hints."""
        for d in [self.models_dir, self.voices_dir, self.logs_dir, str(BASE_DIR / "data")]:
            Path(d).mkdir(parents=True, exist_ok=True)


# Global singleton
config = Config()
