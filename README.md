# Jarvis AI Assistant for Android

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

A modular, voice-controlled AI assistant for Android Termux with a brain-inspired pipeline architecture, neural visualization UI, and 132 passing tests.

## Architecture

The assistant is built as **11 independent pipelines**, organized under clear custom package namespaces at the root level:

| Region | Package Path | Target Module | Function |
|--------|--------------|---------------|----------|
| Prefrontal Cortex (PFC) | `brain/` | `engine.py` | Executive orchestration, intent routing |
| Auditory Cortex | `perception/voice/` | `stt.py` | Groq Whisper STT, wake word detection |
| Wernicke's Area | `ai/` | `chat.py` | Groq LLM + OpenAI fallback, reasoning |
| Broca's Area | `perception/voice/` | `tts.py` | Piper TTS / edge-tts / Android TTS, speech output |
| Motor Cortex | `actions/` | `android.py` | Termux:API Android device control |
| Hippocampus | `memory/` | `storage.py` | SQLite storage (history, facts, notes, reminders) |
| Occipital Cortex | `perception/` | `vision.py` | Camera capture, photo metadata & visual inspection |
| Somatosensory Cortex | `brain/` | `telemetry.py` | System health diagnostics (CPU, RAM, storage) |
| Defense Cortex | `actions/` | `protocols.py` | Stark security protocols (Stealth Mode, house party) |
| Thalamus | `actions/browser/` | `search.py` | DuckDuckGo web search & weather reports |
| Cerebellum | `actions/` | `timers.py` | Async timers, countdowns & background schedulers |

---

## Installation & Setup

We provide an automated setup script to install dependencies, construct a virtual environment, and configure environment templates:

* **Android Termux (Native)**:
  ```bash
  chmod +x setup_termux.sh
  ./setup_termux.sh
  ```

Once setup finishes, edit your `.env` configuration file to input your `GROQ_API_KEY`.

---

## Usage

You can use the automated startup script `start.sh` or run the module packages directly via Python:

### Voice Mode (with wake word)
```bash
./start.sh
# OR
python -m app
```

### Text Mode
```bash
./start.sh --text
# OR
python -m app --text
```

### Text Mode (no TTS)
```bash
./start.sh --no-voice
```

### Terminal UI (Brain Network Monitor)
```bash
./start.sh --tui
```

### Web UI
```bash
./start.sh --web
```
Opens a Flask web server (`http://localhost:5000`) with a live brain visualization, chat log, and browser voice input.

---

## Project Structure

```
Jarvis/
├── app/
│   ├── __main__.py          # python -m app entry point
│   └── cli.py               # CLI parser
├── brain/
│   ├── engine.py            # Orchestrator state machine
│   ├── intent.py            # Rule-based intent classifier (40+ patterns)
│   ├── handlers.py          # Handler registry
│   ├── autonomy.py          # Proactive autonomy background monitor
│   └── telemetry.py         # System health telemetry
├── memory/
│   └── storage.py           # SQLite storage (7 tables)
├── perception/
│   ├── vision.py            # Visual inspection & camera capture
│   └── voice/
│       ├── audio.py         # Sci-fi sound effects synthesis
│       ├── stt.py           # Groq Whisper STT + wake word
│       └── tts.py           # Piper / edge-tts / Android TTS
├── actions/
│   ├── android.py           # Device control
│   ├── timers.py            # Timer scheduler
│   ├── protocols.py         # Stark named security protocols
│   └── browser/
│       └── search.py        # Weather and web search
├── ai/
│   ├── chat.py              # LLM reasoning client
│   └── tools.py             # LLM tool schemas spec
├── ui/
│   ├── brain_renderer.py    # Brain rendering logic
│   ├── terminal/
│   │   └── tui.py           # Curses terminal HUD
│   └── web/
│       ├── app.py           # Flask server
│       ├── static/brain.js  # Canvas neural visualization
│       └── templates/index.html
├── shared/
│   ├── base.py              # Base AsyncPipeline
│   └── logger.py            # Shared logger
├── config/
│   └── settings.py          # .env settings config loader
├── tests/                   # Python unit tests
├── requirements.txt
├── README.md
└── start.sh
```

---

## Running Tests

```bash
.venv/bin/pytest
```

**Current test count: 132 passing** across 20 test files.
