#!/bin/bash
# Installation script for Jarvis AI Assistant on Linux (Debian/Ubuntu-based)
set -e

echo "=== Jarvis AI Assistant Linux Installer ==="

# Install system dependencies
echo "Installing system packages..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libportaudio2 \
    libportaudiocpp2 \
    portaudio19-dev \
    ffmpeg \
    libasound2-dev \
    git

# Create directories
mkdir -p data models voices logs

# Initialize virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

# Upgrade pip and install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
# Install sounddevice requirements
pip install sounddevice numpy

# Configure .env
if [ ! -f ".env" ]; then
    echo "Creating environment file .env..."
    cp .env.example .env
    echo "Please configure the .env file with your Groq and OpenAI API keys."
else
    echo ".env file already exists, skipping."
fi

echo "=== Setup complete! ==="
echo "To run the Jarvis Assistant, execute:"
echo "  source .venv/bin/activate"
echo "  python -m jarvis --web --text"
