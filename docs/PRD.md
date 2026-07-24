# PRD — Jarvis AI Assistant for Android

## 1. Overview

**Product Name:** Jarvis AI Assistant for Android  
**Version:** 0.3.0  
**Author:** Minaty001  
**Repository:** https://github.com/Minaty001/jarvis-ai-assistent-for-android

A voice-controlled AI assistant for Android (Termux) built with a brain-inspired pipeline architecture. Users speak commands, the assistant processes them through a chain of STT → LLM reasoning → device action / TTS response, and visualises its internal state as a live cortical network map.

**Crafted by Minaty001** — made for him, but free for everyone to use.

## 2. Target Audience

- **Android power users** who want hands-free device control (apps, settings, flashlight, wifi, bluetooth, etc.)
- **Termux users** looking for an extensible, voice-driven assistant
- **Developers** interested in modular AI pipeline architectures with graceful degradation

## 3. Problem Statement

Existing Android assistants are closed, cloud-dependent, or not extensible. Users on Termux lack a voice-controlled assistant that:
- Runs with cloud STT via Groq Whisper API (fast, accurate)
- Provides LLM-powered reasoning via Groq API
- Controls Android hardware via termux-api
- Shows real-time internal pipeline state
- Degrades gracefully when components are unavailable

## 4. Core Features

### 4.1 Voice Interaction
- Wake-word activation ("Jarvis", "Boss", "Computer")
- Speech-to-text via **Groq Whisper API** (`whisper-large-v3`)
- LLM-powered chat and reasoning via Groq API (`llama-3.1-8b-instant`)
- Text-to-speech via Piper TTS (local), edge-tts (free cloud), or Android TTS fallback
- Text-only fallback when microphone / STT is unavailable

### 4.2 Android Device Control
- Open / close apps by name (camera, settings, gallery, browser, etc.)
- Toggle flashlight, wifi, bluetooth
- Adjust volume and brightness
- Read battery status, time, date
- Search Google / YouTube
- Take notes, set reminders (with Memory pipeline persistence)

### 4.3 Persistent Memory
- Conversation history (SQLite)
- User facts ("remember my name is Alex")
- Notes and reminders storage
- Context injection into LLM prompts

### 4.4 Real-time Brain Visualization
- Terminal TUI (curses) showing 6 cortical regions with activity glow
- Web UI (Flask) with live SSE updates and canvas-based brain map
- Neural pathway animation during processing
- Per-region latency, activity %, synapse count, cortex health

### 4.5 Graceful Degradation
No single component failure crashes the assistant:
- No Groq key → text-only input with informative error
- No Piper → edge-tts (free cloud TTS), then Android TTS fallback
- No Termux:API → descriptive error per action
- No SQLite → conversation continues without persistence
- No microphone → text-only mode

## 5. User Stories

| ID | Story |
|----|-------|
| US1 | As a user, I want to say "Hey Jarvis" and have the assistant listen for my command. |
| US2 | As a user, I want to ask "what's the time" and hear the current time spoken back. |
| US3 | As a user, I want to say "open the camera" and have the camera app launch. |
| US4 | As a user, I want to ask a general question and get an LLM-generated answer. |
| US5 | As a user, I want the assistant to remember facts about me across sessions. |
| US6 | As a user, I want to see the assistant's internal state in a visual brain UI. |
| US7 | As a user, I want to type commands when voice is not available. |
| US8 | As a user, I want the assistant to keep working even if one component fails. |

## 6. Non-Goals

- Not a replacement for Google Assistant / Bixby
- No wake-word model training — uses simple keyword-spotting on Whisper transcriptions
- No offline STT — all speech recognition is via Groq Whisper API
- No GUI beyond the terminal TUI and Flask web UI — no native Android app
- No streaming LLM responses — all responses are generated and returned as complete text

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Intent classification accuracy | >95% on supported intents |
| STT → response latency | <3s with Groq Whisper + Groq LLM |
| Tests passing | All tests green |
| Graceful degradation scenarios | All failure modes handled |
