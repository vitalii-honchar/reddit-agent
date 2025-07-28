# Multi-stage build for reddit-agent
ARG ARCH=
FROM --platform=${ARCH} python:3.13-alpine AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

FROM --platform=${ARCH} python:3.13-alpine AS runtime

# Re-declare ARG for runtime stage
ARG ARCH=

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY src/ ./src/
COPY prompts/ ./prompts/

# Create entrypoint script
RUN cat > /app/entrypoint.sh << 'EOF'
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
EOF

RUN chmod +x /app/entrypoint.sh

# Expose port for FastAPI (will be ignored for scheduler mode)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]