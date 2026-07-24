# Jarvis AI Assistant for Android

> Crafted by [Minaty001](https://github.com/Minaty001) — made for him, but free for everyone to use.

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

## Documentation

- [PRD](docs/PRD.md) — Project requirements and feature specification
- [Architecture](docs/architecture.md) — App flow, tech stack, folder structure
- [Memory Pipeline](docs/memory.md) — Database schema and API reference

## Running Tests

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

All 51 tests should pass.

## License

MIT
