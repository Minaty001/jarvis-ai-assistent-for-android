# Jarvis AI Assistant for Android

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

A modular, voice-controlled AI assistant for Android Termux with a brain-inspired pipeline architecture and neural visualization UI.

## Architecture

The assistant is built as 11 independent pipelines, each mapped to a brain cortical region:

| Region | Pipeline | Function |
|--------|----------|----------|
| Prefrontal Cortex (PFC) | Engine | Executive orchestration, intent routing |
| Auditory Cortex | Speech | Groq Whisper STT, wake word detection |
| Wernicke's Area | Chat | Groq LLM, reasoning |
| Broca's Area | Voice | Piper TTS / edge-tts / Android TTS, speech output |
| Motor Cortex | Device | Termux:API device control |
| Hippocampus | Memory | SQLite storage |
| Occipital Cortex | Vision | Camera capture, photo metadata & visual inspection |
| Somatosensory Cortex | Telemetry | System health diagnostics (CPU, RAM, storage, battery) |
| Defense Cortex | Protocol | Stark security protocols (House Party, Stealth Mode, Protocol Alpha, Lockdown) |
| Thalamus | Search | Live weather telemetry & DuckDuckGo web intelligence search |
| Cerebellum | Scheduler | Async countdown timers & background callbacks |

10+ bidirectional neural pathways connect the regions, visualized in real-time.

## Features

- **Voice Interaction:** Wake word activation ("Jarvis", "Boss", "Computer")
- **Speech-to-Text:** **Groq Whisper API** (`whisper-large-v3`)
- **LLM Reasoning & Function Calling:** Groq API (`llama-3.1-8b-instant`) with OpenAI-compatible tool specifications (`tools.py`)
- **Text-to-Speech:** Piper TTS (local), edge-tts (free cloud), or Android TTS fallback
- **Android Native Ergonomics:** Clipboard set/get, haptic vibration, toast notification overlays, GPS location tracking, telephony call/SMS dispatch, media hardware keys
- **Custom Voice Command Macros:** Define persistent custom voice shortcuts (e.g. *"add custom command 'morning briefing' to tell weather and get system diagnostics"*)
- **Proactive Autonomy:** Background system telemetry and battery low warning monitor (`autonomy.py`)
- **Stark Security Protocols:** Named MCU protocols (`House Party Protocol`, `Stealth Mode`, `Protocol Alpha`, `Lockdown`, `Overdrive`)
- **Visual Intelligence:** Camera snapshot analysis & image target inspection via termux-camera-photo
- **System Telemetry:** Real-time diagnostics for CPU load, RAM usage, storage space, and battery status
- **Web Intelligence & Weather:** Live weather reports (Open-Meteo / wttr.in) & instant web search snippets
- **Async Countdown Scheduler:** Live countdown timers & scheduled background callbacks
- **Persistent Memory:** SQLite storage for conversation history, user facts, notes, reminders, clipboard history, and location log
- **Brain Visualization UI:** Real-time 11-region visual cortical network map (Terminal TUI + Web UI)

## Installation

### Prerequisites

- Android device with [Termux](https://termux.com/) installed
- [Termux:API](https://wiki.termux.com/wiki/Termux:API) add-on
- Python 3.11+
- [Piper TTS](https://github.com/rhasspy/piper) (optional, for local TTS)
- `edge-tts` auto-installs with the package (free cloud TTS, no key needed)
- **Groq API key** for STT and LLM ([get one free](https://console.groq.com))

### Setup

```bash
# Clone the repository
git clone https://github.com/Minaty001/jarvis-ai-assistent-for-android
cd jarvis-ai-assistent-for-android

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For microphone capture (optional, for voice mode)
pip install sounddevice numpy

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
python -m jarvis --once "execute house party protocol"
```

### Web UI

```bash
python -c "from jarvis.ui.web_ui.app import run_server; run_server(port=2026)"
```

Then open `http://localhost:2026` in a browser.

## Project Structure

```
src/jarvis/
├── __init__.py          # Package version
├── __main__.py          # python -m jarvis entry
├── cli.py               # CLI argument parser
├── core/
│   ├── config.py        # Environment config loader
│   ├── intent.py        # Rule-based intent classifier
│   ├── tools.py         # LLM function calling registry & tool schemas
│   └── engine.py        # Orchestrator state machine
├── pipelines/
│   ├── speech.py        # Groq Whisper STT + wake word
│   ├── chat.py          # Groq LLM client with function calling
│   ├── voice.py         # Piper / edge-tts / Android TTS
│   ├── device.py        # Termux:API device & hardware control
│   ├── memory.py        # SQLite storage (conversations, facts, clipboard, location)
│   ├── vision.py        # Visual inspection & camera capture
│   ├── telemetry.py     # System health & diagnostic reporting
│   ├── protocol.py      # Stark security protocol engine
│   ├── search.py        # Live weather & web intelligence
│   ├── scheduler.py     # Async countdown timers
│   └── autonomy.py      # Proactive background health & battery monitor
├── ui/
│   ├── brain_renderer.py  # 11-region brain visualization engine
│   ├── tui.py             # Curses terminal UI
│   └── web_ui/            # Flask web UI with 11-region arc reactor visualizer
└── utils/
    └── logging.py       # Logger setup
```

## Graceful Degradation

The assistant continues working even when components are unavailable:

- **No Groq API key:** STT and LLM unavailable; falls back to text-only input
- **No microphone:** Text-only mode
- **No Piper binary:** Falls back to edge-tts (free cloud TTS), then Android TTS
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

## License

MIT — Crafted by Minaty001
