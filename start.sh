#!/bin/bash
# J.A.R.V.I.S. AI Assistant Startup Script
# Crafted by Minaty001

# Resolve project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Execute the application
python -m app "$@"
