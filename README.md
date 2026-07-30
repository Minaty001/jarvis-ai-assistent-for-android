# Jarvis AI Assistant for Android & Cloud

> **Crafted by [Minaty001](https://github.com/Minaty001)** — made for him, but free for everyone to use.

A modular, voice-controlled AI assistant for Android Termux, Linux, Windows, and Cloud platforms with a brain-inspired pipeline architecture, neural visualization UI, and 132 passing unit tests.

---

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

## Step-by-Step Setup & Deploy Guide

### 1. Prerequisites (All Environments)
- **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com).
- **Environment File**: Copy `.env.example` to `.env` and set your key:
  ```env
  GROQ_API_KEY=your_groq_api_key_here
  ```

---

### 2. Android (Termux Native)

#### Step 1: Install Termux & Termux:API
1. Download and install **Termux** and **Termux:API** apps from [F-Droid](https://f-droid.org/). *(Do not install from Google Play Store as those packages are deprecated)*.
2. Grant requested storage and notification permissions.

#### Step 2: Clone Repository & Run Installer
Open Termux and execute:
```bash
pkg update && pkg upgrade -y
pkg install git -y
git clone https://github.com/Minaty001/jarvis-ai-assistent-for-android.git
cd jarvis-ai-assistent-for-android
chmod +x setup_termux.sh start.sh
./setup_termux.sh
```

#### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env   # Add your GROQ_API_KEY
```

#### Step 4: Run Assistant
- **Voice Mode**: `./start.sh` or `python -m app`
- **Text Mode**: `./start.sh --text`
- **Web UI Mode**: `./start.sh --web` (Open `http://localhost:5000` in browser)
- **TUI HUD**: `./start.sh --tui`

---

### 3. Linux (Ubuntu / Debian / Arch / Fedora)

#### Step 1: Install System Dependencies
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip git ffmpeg portaudio19-dev
  ```
- **Fedora**:
  ```bash
  sudo dnf install -y python3 python3-pip git ffmpeg portaudio-devel
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S --needed python git ffmpeg portaudio
  ```

#### Step 2: Clone & Virtual Environment Setup
```bash
git clone https://github.com/Minaty001/jarvis-ai-assistent-for-android.git
cd jarvis-ai-assistent-for-android
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt sounddevice numpy
```

#### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key
```

#### Step 4: Run or Deploy as systemd Service
- **Run directly**:
  ```bash
  ./start.sh --web   # Web UI mode
  ./start.sh --text  # Text mode
  ```
- **Deploy as systemd background service**:
  ```bash
  sudo cp jarvis.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now jarvis
  ```

---

### 4. Windows (PowerShell / CMD)

#### Step 1: Install Dependencies
1. Download and install **Python 3.10+** from [python.org](https://www.python.org/downloads/) (Check *"Add Python to PATH"* during installation).
2. Download and install **Git** from [git-scm.com](https://git-scm.com/).
3. Download **FFmpeg** and add its `bin` directory to system PATH environment variable.

#### Step 2: Clone Repository & Create Virtual Environment
Open **PowerShell** as User:
```powershell
git clone https://github.com/Minaty001/jarvis-ai-assistent-for-android.git
cd jarvis-ai-assistent-for-android
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt sounddevice numpy
```

#### Step 3: Configure Environment
```powershell
Copy-Item .env.example .env
# Open .env with Notepad and paste your GROQ_API_KEY
notepad .env
```

#### Step 4: Run Assistant
```powershell
python -m app --web
# Or text mode:
python -m app --text
```

---

### 5. Render.com (Cloud Web Deployment)

Deploy Jarvis as a public web application server on [Render.com](https://render.com).

#### Step 1: Fork/Push Code to GitHub
Ensure your repository is uploaded to your GitHub account.

#### Step 2: Create a Web Service on Render
1. Sign in to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
2. Connect your GitHub repository `jarvis-ai-assistent-for-android`.
3. Fill out the service settings:
   - **Name**: `jarvis-ai-assistant`
   - **Environment**: `Python 3`
   - **Region**: Select closest region
   - **Branch**: `main` (or default branch)
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt sounddevice numpy
     ```
   - **Start Command**:
     ```bash
     python -m app --web
     ```

#### Step 3: Set Environment Variables
Under the **Environment Variables** tab, add:
- `GROQ_API_KEY`: `your_actual_groq_api_key`
- `PORT`: `5000` *(or leave default, Render sets PORT automatically)*

#### Step 4: Deploy & Access
Click **Create Web Service**. Once deployment finishes, open your Render `.onrender.com` URL to access your web interface with live brain network visualizations and chat capabilities.

---

## Usage Summary

| Mode | Command | Description |
|------|---------|-------------|
| Voice Mode | `./start.sh` or `python -m app` | Full voice mode with wake word detection |
| Text Mode | `./start.sh --text` or `python -m app --text` | Interactive command-line chat mode |
| Text (No TTS) | `./start.sh --no-voice` | Text mode without speech output |
| Terminal TUI | `./start.sh --tui` | Terminal HUD Brain Network Monitor |
| Web UI Mode | `./start.sh --web` | Flask server (`http://localhost:5000`) with visual neural brain |

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

