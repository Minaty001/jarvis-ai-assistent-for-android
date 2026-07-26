# Architecture — Jarvis AI Assistant for Android

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

## 1. Design Philosophy: Cortical Network

The assistant's architecture mirrors the human brain. Each capability is an independent **pipeline** mapped to a **cortical region**. A lightweight **Engine** orchestrates data flow between them, mimicking thalamocortical relay. Pipelines are decoupled — they exchange typed data through the engine and know nothing of each other.

## 2. Eleven Cortical Regions

| # | Region | Pipeline | File | Function | Colour |
|---|--------|----------|------|----------|--------|
| 1 | Prefrontal Cortex (PFC) | Engine | `core/engine.py` | Executive orchestration, intent routing | Amber `#ffaa00` |
| 2 | Auditory Cortex | Speech | `pipelines/speech.py` | Groq Whisper STT, wake word detection | Cyan `#00f0ff` |
| 3 | Wernicke's Area | Chat | `pipelines/chat.py` | Groq LLM, reasoning, response generation | Green `#00ff88` |
| 4 | Broca's Area | Voice | `pipelines/voice.py` | Piper TTS / edge-tts / Android TTS, speech output | Purple `#8844ff` |
| 5 | Motor Cortex | Device | `pipelines/device.py` | Termux:API Android device control | Red `#ff3366` |
| 6 | Hippocampus | Memory | `pipelines/memory.py` | SQLite conversation history and facts | Blue `#0066ff` |
| 7 | Occipital Cortex | Vision | `pipelines/vision.py` | Camera capture, photo metadata & visual inspection | Magenta `#ff00ff` |
| 8 | Somatosensory Cortex | Telemetry | `pipelines/telemetry.py` | System health diagnostics (CPU, RAM, storage, battery) | Teal `#00ffcc` |
| 9 | Defense Cortex | Protocol | `pipelines/protocol.py` | Stark security protocols (House Party, Stealth Mode, Protocol Alpha) | Bright Red `#ff3300` |
| 10 | Thalamus | Search | `pipelines/search.py` | Live weather telemetry & DuckDuckGo web search | Yellow `#ffff00` |
| 11 | Cerebellum | Scheduler | `pipelines/scheduler.py` | Async countdown timers & background callbacks | Lime `#aaff00` |

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
| Runtime | Python 3.14 (Termux on aarch64) | Interpreter |
| STT | Groq Whisper API (`whisper-large-v3`) | Speech-to-text |
| LLM | Groq API (`llama-3.1-8b-instant`) | Language model & tool calls |
| Tool Calling | OpenAI JSON Tool Schemas (`tools.py`) | Function calling engine |
| Audio FX | Pure PCM wave synthesizer (`audio_fx.py`) | Multi-modal sci-fi HUD sound effects |
| Autonomy | Background task monitor (`autonomy.py`) | Proactive health & power grid battery alerts |
| TTS | Piper (local) / edge-tts (cloud) / termux-tts-speak | Speech synthesis |
| Device API | termux-api subprocess calls (cached) | Android hardware & ergonomic control |
| Database | SQLite via aiosqlite | Persistence (conversations, facts, clipboard, location, macros) |
| HTTP | httpx (async) | LLM + STT API client |
| Audio | sounddevice + numpy (optional) | Microphone capture |
| Terminal UI | curses (stdlib) | 11-region brain visualization |
| Web UI | Flask + SSE + HTML5 Canvas | 11-region arc reactor visualizer |
| Config | python-dotenv | Environment loading |
| Testing | pytest + pytest-asyncio | Test suite (88 test cases) |

## 5. Folder Structure

```
jarvis-ai-assistent-for-android/
├── pyproject.toml               # Project metadata & dependencies
├── README.md
├── LICENSE                      # MIT License
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
│       │   ├── tools.py         # LLM function calling registry & tool specs
│       │   └── engine.py        # Lightweight orchestrator
│       ├── pipelines/
│       │   ├── speech.py        # Groq Whisper STT + wake word
│       │   ├── chat.py          # Groq LLM client with function calling
│       │   ├── voice.py         # Piper / edge-tts / Android TTS
│       │   ├── device.py        # Termux:API device & hardware control
│       │   ├── memory.py        # SQLite storage (conversations, facts, clipboard, location, custom commands)
│       │   ├── vision.py        # Visual inspection & camera capture
│       │   ├── telemetry.py     # System health & diagnostic reporting
│       │   ├── protocol.py      # Stark security protocol engine
│       │   ├── search.py        # Live weather & web intelligence
│       │   ├── scheduler.py     # Async countdown timers
│       │   ├── autonomy.py      # Proactive background health & battery monitor
│       │   └── audio_fx.py      # Multi-modal PCM sound effect synthesizer
│       ├── ui/
│       │   ├── brain_renderer.py  # 11-region brain visualization engine
│       │   ├── tui.py             # Curses terminal UI
│       │   └── web_ui/
│       │       ├── app.py        # Flask server
│       │       ├── static/brain.js # 11-region arc reactor canvas renderer
│       │       └── templates/index.html
│       └── utils/
│           └── logging.py       # Logger setup
├── tests/
│   ├── test_android_mobile.py
│   ├── test_audio_fx.py
│   ├── test_autonomy.py
│   ├── test_chat.py
│   ├── test_config.py
│   ├── test_custom_commands.py
│   ├── test_device.py
│   ├── test_engine.py
│   ├── test_intent.py
│   ├── test_jarvis_mcu.py
│   ├── test_memory.py
│   ├── test_protocol.py
│   ├── test_scheduler.py
│   ├── test_search.py
│   ├── test_speech.py
│   ├── test_telemetry.py
│   ├── test_tools.py
│   ├── test_vision.py
│   └── test_voice.py
├── data/                        # SQLite database (created at runtime)
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

The intent classifier (`core/intent.py`) is a rule-based regex matcher. It runs **before** the LLM call so that simple device commands bypass the LLM entirely for low latency. Unmatched input falls through to `general_chat` which hits the LLM with tool calling specs (`tools.py`).

**Supported intents:** open_settings, open_camera, open_gallery, open_youtube, open_website, open_app, close_app, go_home, show_recent, show_notifications, flashlight_on/off, volume_up/down, set_volume, brightness_up/down, set_brightness, tell_time, tell_date, battery_status, wifi_on/off, wifi_status, bluetooth_on/off, search_google, play_music, take_note, read_notes, delete_note, set_reminder, view_reminders, delete_reminder, calculate, remember_fact, what_is, who_created, tell_weather, system_telemetry, run_protocol, set_timer, view_timers, cancel_timer, scan_vision, web_search_intel, copy_clipboard, get_clipboard, vibrate_phone, show_toast_msg, get_gps_location, media_control, make_phone_call, send_sms_msg, add_custom_cmd, list_custom_cmds, delete_custom_cmd, exit, general_chat.

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
