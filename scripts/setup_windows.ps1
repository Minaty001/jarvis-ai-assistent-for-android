# PowerShell script to set up Jarvis AI Assistant on Windows
$ErrorActionPreference = "Stop"

Write-Host "=== Jarvis AI Assistant Windows Setup ===" -ForegroundColor Green

# Verify Python is installed
try {
    & python --version | Out-Null
} catch {
    Write-Error "Python is not installed or not in system PATH. Please download and install Python 3.11+."
}

# Create directories
New-Item -ItemType Directory -Force -Path .\data, .\models, .\voices, .\logs | Out-Null

# Setup virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path -Path ".\.venv")) {
    & python -m venv .venv
}

# Activate virtual environment and install packages
Write-Host "Installing python dependencies..." -ForegroundColor Cyan
& .\.venv\Scripts\pip.exe install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt
& .\.venv\Scripts\pip.exe install sounddevice numpy

# Copy environment variables
if (-not (Test-Path -Path ".\.env")) {
    Write-Host "Creating environment file .env..." -ForegroundColor Cyan
    Copy-Item .env.example .env
    Write-Host "Please edit the .env file with your API keys (e.g. GROQ_API_KEY)." -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists."
}

Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host "To start the assistant:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\activate.ps1" -ForegroundColor Cyan
Write-Host "  python -m jarvis --web --text" -ForegroundColor Cyan
