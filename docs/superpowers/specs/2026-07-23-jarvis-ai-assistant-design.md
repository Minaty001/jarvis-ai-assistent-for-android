# Jarvis AI Assistant for Android — Design Specification

## 1. Project Overview

**Name:** Jarvis AI Assistant for Android  
**Description:** A modular, voice-controlled AI assistant for Android Termux, rebuilt from the single-file `jarvis.py` prototype into a proper package with pipeline-based architecture and a brain-inspired neural UI.

**Key Objectives:**
- Voice interaction (Vosk STT → Groq LLM → Piper TTS)
- Android device control via Termux:API
- Persistent memory via SQLite
- A brain-visualization UI showing neural pipelines as cortical regions

---

## 2. Architecture: Cortical Network Design

The architecture maps each capability to a brain region. Pipelines are independent, communicate through typed interfaces, and are orchestrated by a lightweight engine that mirrors thalamocortical relay.

### 2.1 The Six Cortical Regions (Pipelines)

| # | Region | Pipeline | Function | Color |
|---|--------|----------|----------|-------|
| 1 | Prefrontal Cortex (PFC) | `engine.py` | Executive orchestration, intent routing | Amber `#ffaa00` |
| 2 | Auditory Cortex | `speech.py` | Vosk STT, wake word detection | Cyan `#00f0ff` |
| 3 | Wernicke's Area | `chat.py` | Groq LLM, reasoning, response generation | Green `#00ff88` |
| 4 | Broca's Area | `voice.py` | Piper TTS, speech output | Purple `#8844ff` |
| 5 | Motor Cortex | `device.py` | Termux:API device control | Red `#ff3366` |
| 6 | Hippocampus | `memory.py` | SQLite memory, conversation history | Blue `#0066ff` |

### 2.2 Neural Pathways (Data Flow)

10 bidirectional pathways connect the regions:

- **Auditory → Wernicke's** (speech-to-text → LLM): STT output feeds LLM input
- **Wernicke's → Broca's** (LLM → TTS): LLM response feeds TTS
- **Wernicke's → Hippocampus** (LLM → Memory): Responses stored
- **Hippocampus → Wernicke's** (Memory → LLM): Context retrieved for prompts
- **PFC → Wernicke's** (Executive → LLM): Intent classification steers LLM
- **PFC → Motor** (Executive → Device): Intent triggers device actions
- **Wernicke's → PFC** (LLM → Executive): LLM response routed back
- **Motor → PFC** (Device → Executive): Device result reported
- **Broca's → PFC** (TTS → Executive): Speech completion acknowledged
- **Auditory → PFC** (STT → Executive): Wake word / command detected

### 2.3 Engine Orchestration Flow

```
                 ┌──────────────────────────────────────┐
                 │         PFC (Engine/Intent)          │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │ Intent   │  │ Orchestrator     │  │
                 │  │ Classifier│  │ (state machine)  │  │
                 │  └────┬─────┘  └───────┬──────────┘  │
                 └───────┼────────────────┼──────────────┘
                         │                │
    ┌────────────────────┼────────────────┼────────────────────┐
    │                    │                │                    │
    ▼                    ▼                ▼                    ▼
┌─────────┐       ┌──────────┐      ┌──────────┐       ┌──────────┐
│Auditory │──────▶│Wernicke's│──────▶│ Broca's  │       │  Motor   │
│ Cortex  │ STT   │  Area    │  LLM  │  Area    │  TTS  │  Cortex  │
│ (speech)│       │ (chat)   │       │ (voice)  │       │ (device) │
└─────────┘       └────┬─────┘      └──────────┘       └──────────┘
                       │
                       ▼
                  ┌──────────┐
                  │Hippocampus│
                  │ (memory) │
                  └──────────┘
```

---

## 3. Module Structure

```
jarvis-ai-assistent-for-android/
├── pyproject.toml              # Project metadata & dependencies
├── README.md
├── .env.example
├── docs/
│   ├── design/
│   │   ├── brain-architecture.svg     # Static brain SVG
│   │   └── cortical-network-philosophy.md
│   └── superpowers/specs/
│       └── 2026-07-23-jarvis-ai-assistant-design.md
├── src/
│   └── jarvis/
│       ├── __init__.py
│       ├── __main__.py               # Entry: `python -m jarvis`
│       ├── cli.py                     # CLI arg parser & main runner
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py              # .env config loader
│       │   ├── intent.py              # Intent classifier (rule-based)
│       │   └── engine.py              # Lightweight orchestrator
│       ├── pipelines/
│       │   ├── __init__.py
│       │   ├── speech.py              # Vosk STT + wake word
│       │   ├── chat.py                # Groq LLM client
│       │   ├── voice.py               # Piper TTS (with termux-tts fallback)
│       │   ├── device.py              # Termux:API device control
│       │   └── memory.py              # SQLite storage
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── brain_renderer.py      # Brain SVG/ASCII renderer
│       │   ├── tui.py                 # Terminal UI (curses-based)
│       │   └── web_ui/               # Optional: Flask/FastAPI web UI
│       │       ├── __init__.py
│       │       ├── app.py
│       │       ├── static/
│       │       │   └── brain.js       # Interactive brain visualization
│       │       └── templates/
│       │           └── index.html
│       └── utils/
│           ├── __init__.py
│           └── logging.py             # Logging setup
├── tests/
│   ├── __init__.py
│   ├── test_speech.py
│   ├── test_chat.py
│   ├── test_voice.py
│   ├── test_device.py
│   ├── test_memory.py
│   ├── test_intent.py
│   └── test_engine.py
└── requirements.txt
```

---

## 4. Brain Visualization UI

The user specifically requested a UI showing neural networks integrating like a brain image. Two complementary UI modes are specified:

### 4.1 Terminal TUI (Primary — curses-based)

- Real-time brain status panel showing all 6 cortical regions
- Each region glows/animates when active (STT listening → Auditory glows cyan)
- Neural pathway lines flash when data travels between regions
- Shows: active region, latency, neural activity %, cortex status
- Text input/output area at the bottom for fallback interaction
- Responsive to terminal resize
- Color-coded per region palette

### 4.2 Web UI (Secondary — Flask/FastAPI)

- Interactive brain visualization using HTML5 Canvas / SVG
- Clickable regions showing pipeline stats and logs
- Real-time activity indicators via SSE (Server-Sent Events)
- Mobile-responsive layout for Android browser access
- Region tooltips with live metrics

### 4.3 Neural Integration Display

The UI must communicate:
- **Structural:** The 6 regions positioned anatomically (PFC top-center, Auditory left, Wernicke's left-center, Broca's right-center, Motor right, Hippocampus bottom-center)
- **Dynamic:** Active pathways light up during processing — e.g., when user speaks, the chain Auditory → Wernicke's → Broca's lights up in sequence
- **Metrics:** Per-region latency, activity level, synapse count (10 pathways), cortex health status
- **Feedback loop visualization:** Dashed lines for memory formation (Hippocampus ↔ Wernicke's)

---

## 5. Pipeline Specifications

### 5.1 Speech Pipeline (`speech.py`)

**Input:** Microphone audio (16kHz, mono, int16)  
**Output:** Recognized text string | Wake word event  
**Dependencies:** Vosk, sounddevice, numpy  
**Interface:**

```python
class SpeechPipeline:
    async def load_model() -> bool
    async def start()                    # Begin mic capture
    async def stop()                     # Stop mic capture
    async def wait_for_wake() -> bool    # Block until wake word
    async def listen(timeout: float) -> Optional[str]
    def set_on_speech_detected(callback) # For TTS interrupt
```

**Wake words:** "jarvis", "boss", "computer" (configurable)  
**Fallback:** If Vosk unavailable, accept text input via terminal

### 5.2 Chat Pipeline (`chat.py`)

**Input:** Message list (system + user + history)  
**Output:** Response string  
**Dependencies:** httpx  
**Interface:**

```python
class ChatPipeline:
    async def generate(messages: list[dict]) -> Optional[str]
    async def close()
```

**Model:** llama3-8b-8192 (configurable)  
**Temperature:** 0.7  
**Max tokens:** 512  
**Retry:** 2 attempts on rate limit / timeout

### 5.3 Voice Pipeline (`voice.py`)

**Input:** Text string  
**Output:** Spoken audio (via Piper or termux-tts-speak)  
**Interface:**

```python
class VoicePipeline:
    async def speak(text: str)          # Speak + auto-cancel previous
    async def cancel()                  # Interrupt current speech
```

**Primary:** Piper TTS (local, low-latency)  
**Fallback:** termux-tts-speak (Android TTS engine)  
**Final fallback:** Log only

### 5.4 Device Pipeline (`device.py`)

**Input:** Intent name + params dict  
**Output:** Result string  
**Interface:**

```python
class DevicePipeline:
    async def execute(intent: str, params: dict) -> str
    async def has_termux() -> bool
```

**Supported actions:** open/close app, flashlight, volume, brightness, wifi, bluetooth, battery, time/date, search, notes, reminders, calculator, website, music  
**Mechanism:** termux-api subprocess calls via asyncio

### 5.5 Memory Pipeline (`memory.py`)

**Interface:**

```python
class MemoryPipeline:
    async def save_exchange(role: str, content: str)
    async def load_recent(limit: int) -> list[dict]
    async def remember(key: str, value: str)
    async def recall(key: str) -> Optional[str]
    async def get_facts() -> str
    async def build_context(user_msg: str) -> tuple[str, list[dict]]
    async def close()
```

**Tables:** `conversation`, `memory`, `settings`, `notes`, `reminders`  
**Async:** aiosqlite preferred, sync sqlite3 fallback

---

## 6. Engine Specification (`engine.py`)

The engine is not a heavyweight orchestrator — it is a lightweight cortical relay.

```python
class Engine:
    def __init__(self, config)
    async def initialize()         # Load all pipelines
    async def run()                # Main loop
    async def process(text: str)   # Single turn (for testing/CLI)
    async def shutdown()
```

**State machine:**

```
IDLE → WAKE_WORD → LISTENING → PROCESSING → SPEAKING → IDLE
                         │                      │
                         └──→ TEXT_INPUT ←───────┘
```

**Error recovery:** If a pipeline fails, the engine degrades gracefully — continues with available components and reports which functions are offline.

---

## 7. Data Flow: A Single Turn

```
User: "Hey Jarvis, open the camera"

1. [Auditory Cortex] Wake word detected → PFC notified
2. [Auditory Cortex] Records audio → Vosk STT → "open the camera"
3. [Auditory → Wernicke's] Text routed to ChatPipeline
4. [PFC] Intent classifier runs on text → ("open_app", {app_name: "camera"})
5. [Wernicke's → PFC] Intent matched → no LLM call needed
6. [PFC → Motor] Execute open_app("camera")
7. [Motor → PFC] Result: "Camera opened"
8. [PFC → Wernicke's] Generate confirmation text
9. [Wernicke's → Broca's] "Opening the camera now"
10. [Broca's] Piper TTS speaks confirmation
11. [Wernicke's → Hippocampus] Log entire exchange to SQLite
```

---

## 8. Error Handling Strategy

| Failure | Behavior |
|---------|----------|
| Vosk model missing / corrupt | STT pipeline returns False; Engine falls back to text input |
| Microphone unavailable | Speech pipeline logs warning; text-only mode |
| Groq API down | Chat returns None; Engine says "I'm having trouble thinking" |
| Piper binary missing | Voice falls back to termux-tts-speak |
| Termux:API unavailable | Device pipeline returns descriptive error per action |
| SQLite write failure | Memory logs error; conversation continues without persistence |

**General principle:** No single pipeline failure crashes the assistant. Each pipeline has a health-check method the engine polls on startup.

---

## 9. Testing Strategy

| Suite | Scope | Framework |
|-------|-------|-----------|
| Unit: intent | Pattern matching, edge cases | pytest |
| Unit: memory | CRUD operations, context building | pytest + temp db |
| Unit: engine | State machine, intent routing | pytest + mocks |
| Integration | All pipelines with real hardware (manual) | — |
| UI | Terminal rendering, resize handling | pytest + curses mocks |

---

## 10. Implementation Phasing

**Phase 1 — Package scaffold + Core (Week 1)**
- pyproject.toml, module structure, config loader
- Intent classifier tests
- CLI entry point

**Phase 2 — Pipelines (Week 2)**
- Speech pipeline with Vosk
- Chat pipeline with Groq
- Voice pipeline with Piper
- Device pipeline
- Memory pipeline

**Phase 3 — Engine + Integration (Week 3)**
- Engine state machine
- Full integration test
- Error handling hardening

**Phase 4 — Brain UI (Week 4)**
- Terminal TUI with curses brain visualization
- Web UI with interactive brain SVG
- Real-time neural activity display

**Phase 5 — Polish (Week 5)**
- Documentation
- Performance tuning
- Graceful degradation testing

---

## 11. Environment Constraints

- **Runtime:** Python 3.14.4 on aarch64-linux-android (Termux)
- **C compilation:** Unavailable for native extensions (Pillow, cairosvg cannot build)
- **Display:** Terminal-based; no X11/Wayland
- **Audio:** PortAudio via sounddevice; ALSA via aplay
- **Device API:** termux-api package
- **Package manager:** apt/pkg
