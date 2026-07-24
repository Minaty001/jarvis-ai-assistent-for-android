# Architecture — Jarvis AI Assistant for Android

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

## 1. Design Philosophy: Cortical Network

The assistant's architecture mirrors the human brain. Each capability is an independent **pipeline** mapped to a **cortical region**. A lightweight **Engine** orchestrates data flow between them, mimicking thalamocortical relay. Pipelines are decoupled — they exchange typed data through the engine and know nothing of each other.

## 2. Six Cortical Regions

| # | Region | Pipeline | File | Function | Colour |
|---|--------|----------|------|----------|--------|
| 1 | Prefrontal Cortex (PFC) | Engine | `core/engine.py` | Executive orchestration, intent routing | Amber `#ffaa00` |
| 2 | Auditory Cortex | Speech | `pipelines/speech.py` | Groq Whisper STT, wake word detection | Cyan `#00f0ff` |
| 3 | Wernicke's Area | Chat | `pipelines/chat.py` | Groq LLM, reasoning, response generation | Green `#00ff88` |
| 4 | Broca's Area | Voice | `pipelines/voice.py` | Piper TTS / edge-tts / Android TTS, speech output | Purple `#8844ff` |
| 5 | Motor Cortex | Device | `pipelines/device.py` | Termux:API Android device control | Red `#ff3366` |
| 6 | Hippocampus | Memory | `pipelines/memory.py` | SQLite conversation history and facts | Blue `#0066ff` |

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
    9. [Broca's]           Piper TTS speaks confirmation
    10. [Wernicke's → Hippocampus] Log entire exchange to SQLite
```

## 4. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Runtime | Python 3.14 (Termux on aarch64) | Interpreter |
| STT | Groq Whisper API (`whisper-large-v3`) | Speech-to-text |
| LLM | Groq API (`llama-3.1-8b-instant`) | Language model |
| TTS | Piper (local) / edge-tts (cloud) / termux-tts-speak | Speech synthesis |
| Device API | termux-api subprocess calls | Android hardware control |
| Database | SQLite via aiosqlite | Persistence |
| HTTP | httpx (async) | LLM + STT API client |
| Audio | sounddevice + numpy (optional) | Microphone capture |
| Terminal UI | curses (stdlib) | Brain visualisation |
| Web UI | Flask | Browser interface |
| Config | python-dotenv | Environment loading |
| Testing | pytest + pytest-asyncio | Test suite |

## 5. Folder Structure

```
jarvis-ai-assistent-for-android/
├── pyproject.toml               # Project metadata & dependencies
├── README.md
├── .env.example                 # Configuration template
├── docs/
│   ├── PRD.md                   # Project requirements document
│   ├── architecture.md          # This file
│   ├── memory.md                # Memory pipeline documentation
│   └── design/
│       └── brain-architecture.svg
├── src/
│   └── jarvis/
│       ├── __init__.py          # Package version
│       ├── __main__.py          # Entry: python -m jarvis
│       ├── cli.py               # CLI argument parser & runner
│       ├── core/
│       │   ├── config.py        # .env config loader
│       │   ├── intent.py        # Rule-based intent classifier
│       │   └── engine.py        # Lightweight orchestrator
│       ├── pipelines/
│       │   ├── speech.py        # Groq Whisper STT + wake word
│       │   ├── chat.py          # Groq LLM client
│       │   ├── voice.py         # Piper TTS + termux-tts fallback
│       │   ├── device.py        # Termux:API device control
│       │   └── memory.py        # SQLite storage
│       ├── ui/
│       │   ├── brain_renderer.py  # Brain SVG/ASCII renderer
│       │   ├── tui.py             # Curses terminal UI
│       │   └── web_ui/
│       │       ├── app.py        # Flask server
│       │       ├── static/brain.js
│       │       └── templates/index.html
│       └── utils/
│           └── logging.py       # Logger setup
├── tests/
│   ├── test_speech.py
│   ├── test_chat.py
│   ├── test_voice.py
│   ├── test_device.py
│   ├── test_memory.py
│   ├── test_intent.py
│   └── test_engine.py
├── data/                        # SQLite database (created at runtime)
├── models/                      # (Legacy — Vosk model no longer required)
├── voices/                      # Piper TTS voices
└── logs/                        # Log output
```

## 6. Engine State Machine

```
IDLE → WAKE_WORD → LISTENING → PROCESSING → SPEAKING → IDLE
                         │                      │
                         └──→ TEXT_INPUT ←───────┘
```

The engine transitions through states as a voice turn progresses. If the speech pipeline is unavailable it starts in `TEXT_INPUT` mode directly.

## 7. Intent Classification

The intent classifier (`core/intent.py`) is a rule-based regex matcher. It runs **before** the LLM call so that simple device commands bypass the LLM entirely for low latency. Unmatched input falls through to `general_chat` which hits the LLM.

**Supported intents:** open_settings, open_camera, open_gallery, open_youtube, open_website, open_app, close_app, go_home, show_recent, show_notifications, flashlight_on/off, volume_up/down, set_volume, brightness_up/down, set_brightness, tell_time, tell_date, battery_status, wifi_on/off, wifi_status, bluetooth_on/off, search_google, play_music, take_note, read_notes, delete_note, set_reminder, view_reminders, delete_reminder, calculate, remember_fact, what_is, who_created, exit, general_chat.

## 8. Graceful Degradation

| Failure | Behaviour |
|---------|-----------|
| Groq API key missing | STT + LLM return informative error; text-only mode |
| Microphone unavailable | Speech pipeline logs warning; text-only mode |
| Groq API down | Chat returns `None`; Engine says "I'm having trouble thinking" |
| Piper binary missing | Voice falls back to edge-tts, then termux-tts-speak |
| Termux:API unavailable | Device returns descriptive error string per action |
| SQLite write failure | Memory logs error; conversation continues without persistence |

## 9. Configuration

All configuration is via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (required for LLM + STT) |
| `MODEL_NAME` | `llama-3.1-8b-instant` | LLM model |
| `WAKE_WORDS` | `jarvis,boss,computer` | Comma-separated wake words |
| `SAMPLE_RATE` | `16000` | Audio sample rate |
| `LISTEN_TIMEOUT` | `5.0` | STT listen timeout (seconds) |
| `GROQ_TIMEOUT` | `30.0` | LLM API timeout |
| `MAX_HISTORY` | `20` | Conversation turns to include in context |
| `TTS_RATE` / `TTS_PITCH` | `175` / `100` | Android TTS parameters |

## 10. Creator

This project was **crafted by Minaty001** — an AI assistant made for personal use, but shared freely. When asked "who created you?", Jarvis responds: *"Minaty001 made me for him, but you can use me too!"*
