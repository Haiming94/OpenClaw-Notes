#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "envs" ]; then
    source envs/bin/activate
else
    echo "envs not found, run ./setup.sh first"
    exit 1
fi

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo ".env not found, run ./setup.sh first"
    exit 1
fi

PORT="${STREAMLIT_PORT:-8001}"

echo "Multi-Agent Research Studio"
echo "==========================================="
echo "Gateway: ${OPENCLAW_GATEWAY_URL}"
echo "Streamlit: http://localhost:${PORT}"
echo "==========================================="

streamlit run ui/app.py \
    --server.port "$PORT" \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.primaryColor "#6C63FF" \
    --theme.backgroundColor "#0E1117" \
    --theme.secondaryBackgroundColor "#1A1F2E" \
    --theme.textColor "#FAFAFA"
