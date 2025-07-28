#!/bin/sh
set -e

if [ "$MODE" = "api" ]; then
    echo "Starting FastAPI server with gunicorn (4 workers)..."
    exec gunicorn src/agentapi/main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
elif [ "$MODE" = "scheduler" ]; then
    echo "Starting scheduler..."
    exec python src/scheduler/main.py
else
    echo "Error: MODE must be either 'api' or 'scheduler'"
    exit 1
fi