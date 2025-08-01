#!/bin/bash
set -e

# Default values
MODE=${MODE:-agentapi}
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Starting Reddit Agent in ${MODE} mode on ${HOST}:${PORT}"

case "${MODE}" in
    "agentapi")
        echo "Launching AgentAPI service..."
        exec fastapi run src/agentapi/main.py --port "${PORT}" --host "${HOST}"
        ;;
    "insights")
        echo "Launching Insights service..."
        exec fastapi run src/insights/main.py --port "${PORT}" --host "${HOST}"
        ;;
    *)
        echo "Error: Unknown MODE '${MODE}'. Supported modes: agentapi, insights"
        echo "Usage: docker run -e MODE=<agentapi|insights> <image>"
        exit 1
        ;;
esac