# Architecture — Jarvis AI Assistant for Android

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

## 1. Design Philosophy: Cortical Network

The assistant's architecture mirrors the human brain. Each capability is an independent **pipeline** mapped to a **cortical region**. A lightweight **Engine** orchestrates data flow between them, mimicking thalamocortical relay. Pipelines are decoupled — they exchange typed data through the engine and know nothing of each other.

## 2. Eleven Cortical Regions

| # | Region | Pipeline | File | Function | Colour |
|---|--------|----------|------|----------|--------|
| 1 | Prefrontal Cortex (PFC) | Engine | `brain/engine.py` | Executive orchestration, intent routing | Amber `#ffaa00` |
| 2 | Auditory Cortex | Speech | `perception/voice/stt.py` | Groq Whisper STT, wake word detection | Cyan `#00f0ff` |
| 3 | Wernicke's Area | Chat | `ai/chat.py` | Groq LLM + OpenAI fallback, reasoning, tool calling | Green `#00ff88` |
| 4 | Broca's Area | Voice | `perception/voice/tts.py` | Piper TTS / edge-tts / Android TTS, speech output | Purple `#8844ff` |
| 5 | Motor Cortex | Device | `actions/android.py` | Termux:API Android device control | Red `#ff3366` |
| 6 | Hippocampus | Memory | `memory/storage.py` | SQLite history, facts, notes, reminders, clipboard, location | Blue `#0066ff` |
| 7 | Occipital Cortex | Vision | `perception/vision.py` | Camera capture, photo metadata & visual inspection | Magenta `#ff00ff` |
| 8 | Somatosensory Cortex | Telemetry | `brain/telemetry.py` | System health diagnostics (CPU, RAM, storage, battery) | Teal `#00ffcc` |
| 9 | Defense Cortex | Protocol | `actions/protocols.py` | Stark security protocols (House Party, Stealth Mode, Protocol Alpha, Lockdown, Overdrive) | Bright Red `#ff3300` |
| 10 | Thalamus | Search | `actions/browser/search.py` | Live weather telemetry & DuckDuckGo web search | Yellow `#ffff00` |
| 11 | Cerebellum | Scheduler | `actions/timers.py` | Async countdown timers (one-shot + recurring) & background callbacks | Lime `#aaff00` |

## 3. Data Flow — Single Voice Turn

```
User: "Hey Jarvis, open the camera"

    1. [Auditory Cortex]  Wake word detected in Whisper transcript → PFC notified
    2. [Auditory Cortex]  Records audio → Groq Whisper API → "open the camera"
    3. [Auditory → PFC]   Text routed to Engine
    4. [PFC]              Intent classifier runs → ("open_app", {app_name: "camera"})
    5. [PFC → Motor]      Execute open_app("camera") via termux-api
    6. [Motor → PFC]      Result: "Camera opened"
    7. [PFC → Wernicke's] Generate confirmation text via LLM
    8. [Wernicke's → Broca's] "Opening the camera now"
    9. [Broca's]           TTS (Piper → edge-tts → Android) speaks confirmation
    10. [Wernicke's → Hippocampus] Log entire exchange to SQLite
```

## 4. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Runtime | Python 3.12 (Termux on aarch64) | Interpreter |
| STT | Groq Whisper API (`whisper-large-v3`) | Speech-to-text |
| LLM (primary) | Groq API (`llama-3.1-8b-instant`) | Language model & tool calls |
| LLM (fallback) | OpenAI-compatible API (`gpt-4o-mini`) | Automatic failover LLM |
| Tool Calling | OpenAI JSON Tool Schemas (`tools.py`) | 9 dynamic tools for LLM |
| Multi-LLM | Dual provider in `chat.py` | Groq primary, OpenAI fallback with configurable model & base URL |
| Audio FX | Pure PCM wave synthesizer (`audio.py`) | Multi-modal sci-fi HUD sound effects |
| Autonomy | Background task monitor (`autonomy.py`) | Proactive health & power grid battery alerts |
| TTS | Piper (local) / edge-tts (cloud) / termux-tts-speak | Speech synthesis |
| Device API | termux-api subprocess calls (cached) | Android hardware & ergonomic control |
| Database | SQLite via aiosqlite | Persistence (7 tables) |
| HTTP | httpx (async) | LLM + STT API client |
| Audio | sounddevice + numpy (optional) | Microphone capture |
| Terminal UI | curses (stdlib) | 11-region brain visualization |
| Web UI | Flask + SSE + HTML5 Canvas | 11-region brain visualizer with chat log & browser voice input |
| Config | python-dotenv | Environment loading |
| Testing | pytest + pytest-asyncio | Test suite (132 test cases across 20 files) |

## 5. Folder Structure

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

## 6. Creator

This project was **crafted by Minaty001** — an AI assistant made for personal use, but shared freely. When asked "who created you?", Jarvis responds: *"I was designed and built by Minaty001, sir — an architect of considerable talent. I exist to serve."*
