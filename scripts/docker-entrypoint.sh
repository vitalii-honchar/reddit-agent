#!/bin/sh
set -e

# Default values
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Starting Reddit Agent Platform (Modular Monolith) on ${HOST}:${PORT}"

# Run database migrations if DB URL is provided
if [ -n "${INDIE_HACKERS_AGENT_DB_URL:-}" ]; then
    echo "Running database migrations..."
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

echo "Launching unified Reddit Agent Platform..."
exec fastapi run src/app/main.py --port "${PORT}" --host "${HOST}"