#!/data/data/com.termux/files/usr/bin/bash
# Installation script for Jarvis AI Assistant on Android Termux
set -e

echo "=== Jarvis AI Assistant Termux Installer ==="

# Update packages
echo "Updating package lists..."
pkg update -y && pkg upgrade -y

# Install Termux requirements
echo "Installing package dependencies..."
pkg install -y \
    python \
    clang \
    make \
    pkg-config \
    ndk-sysroot \
    libportaudio \
    ffmpeg \
    termux-api \
    git

# Create directories
mkdir -p data models voices logs

# Initialize virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies (since wheel builds might fail, Termux sometimes needs clang flags)
echo "Installing requirements..."
pip install -r requirements.txt
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
echo "Ensure you have the 'Termux:API' app installed from F-Droid."
echo "To run the Jarvis Assistant, execute:"
echo "  source .venv/bin/activate"
echo "  python -m jarvis"
