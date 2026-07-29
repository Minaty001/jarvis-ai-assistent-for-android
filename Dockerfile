# Dockerfile for Jarvis AI Assistant for Android
FROM python:3.11-slim

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (including audio, compiler tools for sounddevice/numpy if built from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libportaudio2 \
    libportaudiocpp2 \
    portaudio19-dev \
    ffmpeg \
    libasound2-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code and other directories
COPY src/ ./src
COPY data/ ./data
COPY models/ ./models
COPY voices/ ./voices
COPY logs/ ./logs

# Expose the Flask Web UI port
EXPOSE 5000

# Set environment variables defaults
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

# Run Flask Web UI by default
CMD ["python", "-m", "jarvis", "--web", "--no-voice"]
