#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Multi-Agent Research Studio - Setup"
echo "==========================================="

if ! command -v python3 &> /dev/null; then
    echo "python3 not found, please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $PYTHON_VERSION"

if [ ! -d "envs" ]; then
    echo "Creating virtual environment..."
    python3 -m venv envs
fi
source envs/bin/activate
echo "envs activated"

echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "Dependencies installed"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env created from .env.example - please edit it"
else
    echo ".env exists"
fi

mkdir -p data/sessions
echo "Data directories ready"

echo ""
echo "==========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Gateway URL and token"
echo "  2. Copy openclaw_config/openclaw.json to ~/.openclaw/openclaw.json"
echo "  3. Start gateway: openclaw gateway"
echo "  4. Start UI: ./start.sh"
echo "==========================================="
