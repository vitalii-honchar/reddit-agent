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
COPY scripts/docker-entrypoint.sh /app/entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port for FastAPI (will be ignored for scheduler mode)
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]