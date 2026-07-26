# Jarvis AI Assistant for Android

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

A modular, voice-controlled AI assistant for Android Termux with a brain-inspired pipeline architecture, neural visualization UI, and 131 passing tests.

## Architecture

The assistant is built as **11 independent pipelines**, each mapped to a brain cortical region:

| Region | Pipeline | Function |
|--------|----------|----------|
| Prefrontal Cortex (PFC) | Engine | Executive orchestration, intent routing |
| Auditory Cortex | Speech | Groq Whisper STT, wake word detection |
| Wernicke's Area | Chat | Groq LLM + OpenAI fallback, reasoning, tool calling |
| Broca's Area | Voice | Piper TTS / edge-tts / Android TTS, speech output |
| Motor Cortex | Device | Termux:API Android device control |
| Hippocampus | Memory | SQLite storage (history, facts, notes, reminders, clipboard, location) |
| Occipital Cortex | Vision | Camera capture, photo metadata & visual inspection |
| Somatosensory Cortex | Telemetry | System health diagnostics (CPU, RAM, storage, battery) |
| Defense Cortex | Protocol | Stark security protocols (House Party, Stealth Mode, Lockdown, Overdrive) |
| Thalamus | Search | Live weather telemetry & DuckDuckGo web intelligence search |
| Cerebellum | Scheduler | Async countdown timers, recurring timers & background callbacks |

10+ bidirectional neural pathways connect the regions, visualized in real-time.

## Features

- **Voice Interaction:** Wake word activation ("Jarvis", "Boss", "Computer")
- **Speech-to-Text:** **Groq Whisper API** (`whisper-large-v3`)
- **Dual LLM Support:** Groq API (`llama-3.1-8b-instant`) primary with **OpenAI-compatible fallback** — automatic failover when one provider is unavailable
- **LLM Function Calling:** OpenAI-compatible JSON tool schemas (`tools.py`) for 9 dynamic tools: clipboard, notes, reminders, web search, weather, location, SMS, media control, telephony
- **Text-to-Speech:** Piper TTS (local), edge-tts (free cloud), or Android TTS fallback
- **Android Device Control:** Open/close apps, flashlight, wifi, bluetooth, volume, brightness, media keys, GPS, clipboard, toast notifications, haptic vibration, phone calls, SMS
- **5 Additional Device Commands:** Screenshot capture, persistent notifications, airplane mode toggle, do not disturb mode, sensor data reading
- **Custom Voice Command Macros:** Define persistent custom voice shortcuts (e.g. *"add custom command 'morning briefing' to tell weather and get system diagnostics"*)
- **Proactive Autonomy:** Background system telemetry and battery low warning monitor (`autonomy.py`)
- **Stark Security Protocols:** Named MCU protocols (`House Party Protocol`, `Stealth Mode`, `Protocol Alpha`, `Lockdown`, `Overdrive`) with audio FX
- **Visual Intelligence:** Camera snapshot analysis & image target inspection via termux-camera-photo
- **System Telemetry:** Real-time diagnostics for CPU load, RAM usage, storage space, and battery status
- **Web Intelligence & Weather:** Live weather reports (Open-Meteo / wttr.in) & instant web search snippets
- **Async Timer System:** One-shot countdown timers and **recurring/repeating timers** with voice alerts and audio FX on expiry
- **Persistent Memory:** SQLite storage with 7 tables — conversation history, user facts, notes, reminders, clipboard history, location log, custom commands
- **Conversation Search & Export:** Search conversation history by keyword, export full history to text file
- **Configurable LLM Parameters:** Adjust temperature and max tokens via `.env`
- **Audio FX Pipeline:** Zero-dependency sci-fi sound effects (`wake`, `protocol`, `success`, `warning`) via PCM wave synthesis
- **Brain Visualization UI:** Real-time 11-region cortical network map with neural pathway animation, available as:
  - **Terminal TUI** (curses-based)
  - **Web UI** (Flask + SSE + HTML5 Canvas) with chat log and browser voice input

## Installation

### Prerequisites

- Android device with [Termux](https://termux.com/) installed
- [Termux:API](https://wiki.termux.com/wiki/Termux:API) add-on
- Python 3.11+
- [Piper TTS](https://github.com/rhasspy/piper) (optional, for local TTS)
- `edge-tts` auto-installs with the package (free cloud TTS, no key needed)
- **Groq API key** for STT and LLM ([get one free](https://console.groq.com))
- **OpenAI API key** (optional, for LLM fallback)

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
# Edit .env and add your GROQ_API_KEY (and optional OPENAI_API_KEY)

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

### Text Mode (no TTS)

```bash
python -m jarvis --no-voice
```

### Terminal UI (Brain Network Monitor)

```bash
python -m jarvis --tui
```

Launches a real-time curses-based 11-region cortical brain map alongside the assistant.

### Web UI

```bash
python -m jarvis --web
```

Opens a Flask web server (`http://0.0.0.0:5000`) with a live brain visualization, chat conversation log, and browser voice input via Web Speech API.

### Combine Flags

```bash
python -m jarvis --text --tui --web
```

### Single Query

```bash
python -m jarvis --once "execute house party protocol"
```

## Project Structure

```
src/jarvis/
├── __init__.py          # Package version
├── __main__.py          # python -m jarvis entry
├── cli.py               # CLI argument parser
├── core/
│   ├── config.py        # Environment config loader
│   ├── intent.py        # Rule-based intent classifier (40+ patterns)
│   ├── tools.py         # LLM function calling registry & tool schemas (9 tools)
│   └── engine.py        # Orchestrator state machine
├── pipelines/
│   ├── speech.py        # Groq Whisper STT + wake word
│   ├── chat.py          # Groq LLM + OpenAI fallback with function calling
│   ├── voice.py         # Piper / edge-tts / Android TTS
│   ├── device.py        # Termux:API device & hardware control (25+ actions)
│   ├── memory.py        # SQLite storage (7 tables, 20+ methods)
│   ├── vision.py        # Visual inspection & camera capture
│   ├── telemetry.py     # System health & diagnostic reporting
│   ├── protocol.py      # Stark security protocol engine
│   ├── search.py        # Live weather & web intelligence
│   ├── scheduler.py     # Async countdown timers (one-shot + recurring)
│   ├── audio_fx.py      # PCM wave sound effect synthesizer
│   └── autonomy.py      # Proactive background health & battery monitor
├── ui/
│   ├── brain_renderer.py  # 11-region brain visualization engine
│   ├── tui.py             # Curses terminal UI
│   └── web_ui/            # Flask web UI with chat log & voice input
└── utils/
    └── logging.py       # Logger setup
```

## Configuration

All configuration is via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (required for LLM + STT primary) |
| `OPENAI_API_KEY` | — | OpenAI API key (optional, LLM fallback) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model for fallback |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible endpoint |
| `MODEL_NAME` | `llama-3.1-8b-instant` | Groq LLM model |
| `LLM_TEMPERATURE` | `0.7` | LLM response temperature |
| `LLM_MAX_TOKENS` | `512` | LLM max tokens per response |
| `WAKE_WORDS` | `jarvis,boss,computer` | Comma-separated wake words |
| `SAMPLE_RATE` | `16000` | Audio sample rate |
| `LISTEN_TIMEOUT` | `5.0` | STT listen timeout (seconds) |
| `GROQ_TIMEOUT` | `30.0` | LLM API timeout |
| `MAX_HISTORY` | `20` | Conversation turns to include in context |
| `TTS_RATE` / `TTS_PITCH` | `175` / `100` | Android TTS parameters |

## Graceful Degradation

The assistant continues working even when components are unavailable:

- **No Groq API key:** Falls back to OpenAI if configured; otherwise STT and LLM unavailable with informative error
- **No OpenAI key either:** Text-only mode, LLM returns structured error
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
# From the project root with virtual environment active
PYTHONPATH=src python -m pytest tests/ -v

# Or using the venv directly
PYTHONPATH=src ./venv/bin/python -m pytest tests/ -v
```

**Current test count: 131 passing** across 19 test files.

## License

MIT — Crafted by Minaty001
