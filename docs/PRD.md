# PRD — Jarvis AI Assistant for Android

## 1. Overview

**Product Name:** Jarvis AI Assistant for Android  
**Version:** 0.5.0  
**Author:** Minaty001  
**Repository:** https://github.com/Minaty001/jarvis-ai-assistent-for-android

A voice-controlled AI assistant for Android (Termux) built with a brain-inspired pipeline architecture. Users speak commands, the assistant processes them through a chain of STT → LLM reasoning → device action / TTS response, and visualises its internal state as a live cortical network map.

**Crafted by Minaty001** — made for him, but free for everyone to use.

## 2. Target Audience

- **Android power users** who want hands-free device control (apps, settings, flashlight, wifi, bluetooth, etc.)
- **Termux users** looking for an extensible, voice-driven assistant
- **Developers** interested in modular AI architectures with graceful degradation

## 3. Problem Statement

Existing Android assistants are closed, cloud-dependent, or not extensible. Users on Termux lack a voice-controlled assistant that:
- Runs with cloud STT via Groq Whisper API (fast, accurate)
- Provides LLM-powered reasoning via Groq API with OpenAI-compatible fallback
- Controls Android hardware via termux-api
- Shows real-time internal pipeline state
- Degrades gracefully when components are unavailable

## 4. Core Features

### 4.1 Voice Interaction
- Wake-word activation ("Jarvis", "Boss", "Computer")
- Speech-to-text via **Groq Whisper API** (`whisper-large-v3`)
- Dual LLM reasoning: **Groq API** (`llama-3.1-8b-instant`) primary with **OpenAI-compatible fallback** (`gpt-4o-mini` or custom) — automatic failover when one provider is unavailable
- LLM function calling with 9 dynamic tool schemas (clipboard, notes, reminders, web search, weather, location, SMS, media control, telephony)
- Text-to-speech via Piper TTS (local), edge-tts (free cloud), or Android TTS fallback
- Text-only fallback when microphone / STT is unavailable

### 4.2 Android Device Control
- Open / close apps by name (camera, settings, gallery, browser, etc.)
- Toggle flashlight, wifi, bluetooth, airplane mode, do not disturb
- Adjust volume and brightness
- Read battery status, time, date
- Search Google / YouTube
- Take notes, set reminders (with Memory database persistence)
- Screenshot capture via termux-api
- Persistent Android notifications via termux-notification
- Sensor data reading (accelerometer, gyroscope, magnetometer, light, pressure, proximity, humidity)
- Clipboard management (copy & read clipboard)
- Haptic vibration feedback
- Android toast overlay notifications
- GPS & location telemetry
- Phone dialing and SMS dispatch
- Media playback controls (play, pause, next, previous, stop)

### 4.3 Persistent Memory
- Conversation history (SQLite) with keyword search and full export to text file
- User facts ("remember my name is Alex")
- Notes and reminders storage
- Clipboard history log
- Device location log
- Custom voice command macros
- Context injection into LLM prompts

### 4.4 Real-time Brain Visualization
- Terminal TUI (curses) showing 11 cortical regions with activity glow
- Web UI (Flask) with live SSE updates and canvas-based brain map
- Persistent scrollable chat conversation log in web UI
- Browser voice input via Web Speech API
- Neural pathway animation during processing
- Per-region latency, activity %, synapse count, cortex health

### 4.5 Stark MCU Tactical & Sensory Capabilities
- **Named Security Protocols:** Execute automated tactical routines (`House Party Protocol`, `Stealth Mode`, `Protocol Alpha`, `Lockdown`, `Overdrive`).
- **Visual Intelligence:** Photo capture and optical target analysis via `termux-camera-photo`.
- **System Telemetry:** Real-time diagnostics monitoring CPU load average, RAM utilization, storage space, and battery status.
- **Web Intelligence & Live Weather:** Instant weather telemetry (Open-Meteo / wttr.in) and real-time DuckDuckGo web search summaries.
- **Async Countdown & Recurring Scheduler:** One-shot countdown timers plus repeating/recurring timers with async completion callbacks and voice alerts.

### 4.6 Android Native Mobile Ergonomics
- **Clipboard Management:** Copy generated answers or read clipboard contents via `termux-clipboard-set` and `termux-clipboard-get`.
- **Haptic Vibration Feedback:** Physical device buzzes via `termux-vibrate`.
- **Android Toast Overlays:** Popup notifications rendered over active Android apps via `termux-toast`.
- **GPS & Location Telemetry:** Query real-time GPS coordinates via `termux-location`.
- **Telephony & Direct SMS:** Direct phone dialing and text message dispatch via `termux-telephony-call` and `termux-sms-send`.
- **Media Hardware Controls:** Playback controls (`play`, `pause`, `next`, `previous`, `stop`).

### 4.7 Custom Voice Commands & Dynamic Tool Calling
- **Custom Macro Shortcuts:** Create persistent voice shortcuts (`"add custom command 'morning briefing' to tell weather and get system diagnostics"`).
- **LLM Function Calling Engine:** OpenAI-compatible JSON tool specifications (`tools.py`) dynamically invoked by Groq LLM during conversational reasoning.
- **Synthesized Audio FX Pipeline:** Zero-dependency sci-fi sound effects (`wake`, `protocol`, `success`, `warning`) generated via standard PCM wave synthesis.
- **Proactive Background Autonomy:** Periodic telemetry monitoring with automated voice alerts when battery power drops below 15% (`autonomy.py`).

### 4.8 Configurable LLM Parameters
- **Temperature:** Adjust LLM response creativity via `LLM_TEMPERATURE` (default 0.7).
- **Max Tokens:** Control response length via `LLM_MAX_TOKENS` (default 512).
- **OpenAI Endpoint:** Configurable base URL for OpenAI-compatible providers (`OPENAI_BASE_URL`).
- **Model Selection:** Separate model config for Groq (`MODEL_NAME`) and OpenAI (`OPENAI_MODEL`).

### 4.9 Graceful Degradation
No single component failure crashes the assistant:
- No Groq key → fails over to OpenAI if configured; otherwise STT and LLM unavailable with informative error
- No Piper → edge-tts (free cloud TTS), then Android TTS fallback
- No Termux:API → descriptive error per action
- No SQLite → conversation continues without persistence
- No microphone → text-only mode
