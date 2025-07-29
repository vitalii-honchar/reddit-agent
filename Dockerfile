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

# Install runtime dependencies for compiled packages
RUN apk add --no-cache libgcc

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY src/ ./src/
COPY prompts/ ./prompts/

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI with integrated scheduler
CMD ["fastapi", "run", "src/agentapi/main.py", "--port", "8000", "--host", "0.0.0.0"]