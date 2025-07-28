#!/bin/sh
set -e

if [ "$MODE" = "api" ]; then
    echo "Starting FastAPI server..."
    exec python -m src.agentapi.main
elif [ "$MODE" = "scheduler" ]; then
    echo "Starting scheduler..."
    exec python src/scheduler/main.py
else
    echo "Error: MODE must be either 'api' or 'scheduler'"
    exit 1
fi