# Deployment and Run Guide

This guide details how to build, deploy, and run the Jarvis AI Assistant across different environments (**Android Termux, Windows, and Linux**), both **with Docker** and **without Docker**.

---

## Quick Reference Commands

| Platform | Without Docker (Local) | With Docker |
| :--- | :--- | :--- |
| **Android Termux** | `./setup_termux.sh` && `./start.sh` | *Not recommended natively (requires root/Proot)* |
| **Linux** | `pip install -e .` && `./start.sh --web --text` | `docker-compose up --build -d` |
| **Windows** | `pip install -e .` && `python -m app --web --text` | `docker-compose up --build -d` |

---

## 1. Setup Without Docker

### Android Termux (Native)
Android Termux runs the assistant directly using Termux packages and Python.

1. **Install and Configure Termux:API**:
   - Download **Termux** and **Termux:API** from F-Droid (do not use Google Play versions as they are outdated).
   - In Termux, run:
     ```bash
     chmod +x setup_termux.sh
     ./setup_termux.sh
     ```
2. **Launch**:
   ```bash
   ./start.sh
   ```

### Linux (Ubuntu/Debian)
1. **Install Package**:
   ```bash
   .venv/bin/pip install -e ".[stt,dev]"
   ```
2. **Launch**:
   ```bash
   ./start.sh --web --text
   ```

### Windows (Native)
1. **Install Package**:
   ```powershell
   .venv\Scripts\pip install -e ".[stt,dev]"
   ```
2. **Launch**:
   ```powershell
   .venv\Scripts\python -m app --web --text
   ```

---

## 2. Setup With Docker

Docker containers run the application in an isolated environment. Note that hardware audio integration (microphone/speakers) inside containers is complex and platform-dependent, so by default, the Docker setup runs in **Web UI/Text mode** (`--web --no-voice`).

### Prerequisites
- Docker and Docker Compose installed.

### Build and Run with Docker Compose
To build and start the Jarvis Assistant container:
```bash
docker-compose up --build -d
```
Once started, the Web UI will be available at `http://localhost:5000`.

### Run via Docker CLI (Standalone)
If you prefer running without Compose:
1. **Build the image**:
   ```bash
   docker build -t jarvis-assistant .
   ```
2. **Run the container**:
   ```bash
   docker run -d \
     -p 5000:5000 \
     --env-file .env \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/models:/app/models \
     -v $(pwd)/voices:/app/voices \
     -v $(pwd)/logs:/app/logs \
     --name jarvis-assistant \
     jarvis-assistant
   ```

---

## 3. Configuration (`.env`)

Create a `.env` file from the template and fill in your keys:
```bash
cp .env.example .env
```
Ensure to add your `GROQ_API_KEY` to enable the primary LLM reasoning.
