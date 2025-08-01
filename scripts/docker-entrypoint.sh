#!/bin/sh
set -e

# Default values
MODE=${MODE:-agentapi}
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Starting Reddit Agent in ${MODE} mode on ${HOST}:${PORT}"

# Run database migrations if DB URL is provided
if [ -n "${INDIE_HACKERS_AGENT_DB_URL:-}" ]; then
    echo "Running database migrations..."
    echo "Using database URL: ${INDIE_HACKERS_AGENT_DB_URL}"
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "Database migrations completed successfully"
    else
        echo "Database migrations failed"
        exit 1
    fi
else
    echo "No database URL provided (INDIE_HACKERS_AGENT_DB_URL), skipping migrations"
fi

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