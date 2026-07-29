# Deployment and Run Guide

This guide details how to build, deploy, and run the Jarvis AI Assistant across different environments (**Android Termux, Windows, and Linux**), both **with Docker** and **without Docker**.

---

## Quick Reference Commands

| Platform | Without Docker (Local) | With Docker |
| :--- | :--- | :--- |
| **Android Termux** | `./scripts/setup_termux.sh` && `python -m jarvis` | *Not recommended natively (requires root/Proot)* |
| **Linux** | `./scripts/setup_linux.sh` && `python -m jarvis --web` | `docker-compose up --build -d` |
| **Windows** | `.\scripts\setup_windows.ps1` && `python -m jarvis` | `docker-compose up --build -d` |

---

## 1. Setup Without Docker

### Android Termux (Native)
Android Termux runs the assistant directly using Termux packages and Python.

1. **Install and Configure Termux:API**:
   - Download **Termux** and **Termux:API** from F-Droid (do not use Google Play versions as they are outdated).
   - In Termux, run:
     ```bash
     chmod +x scripts/setup_termux.sh
     ./scripts/setup_termux.sh
     ```
2. **Launch**:
   ```bash
   source .venv/bin/activate
   python -m jarvis
   ```

### Linux (Ubuntu/Debian)
1. **Run Installation Script**:
   ```bash
   chmod +x scripts/setup_linux.sh
   ./scripts/setup_linux.sh
   ```
2. **Launch**:
   ```bash
   source .venv/bin/activate
   python -m jarvis --web --text
   ```

### Windows (Native)
1. **Run Setup PowerShell Script**:
   Open PowerShell in the project directory and run:
   ```powershell
   Unblock-File .\scripts\setup_windows.ps1
   .\scripts\setup_windows.ps1
   ```
2. **Launch**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m jarvis --web --text
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

Whichever way you deploy, create a `.env` file from the template and fill in your keys:
```bash
cp .env.example .env
```
Ensure to add your `GROQ_API_KEY` to enable the primary LLM pipeline.
