# Multi-stage build for reddit-agent
ARG ARCH=
FROM --platform=${ARCH} python:3.13-alpine AS builder

# Install build dependencies for Rust-based packages
RUN apk add --no-cache gcc musl-dev rust cargo

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

FROM --platform=${ARCH} python:3.13-alpine AS runtime

# Re-declare ARG for runtime stage
ARG ARCH=

# Install runtime dependencies for compiled packages and curl for healthcheck
RUN apk add --no-cache libgcc curl

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code and resources
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY static/ ./static/
COPY templates/ ./templates/
COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini
COPY scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh

# Make entrypoint script executable
RUN chmod +x ./scripts/docker-entrypoint.sh

# Expose port for FastAPI
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint script to support multiple services
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]