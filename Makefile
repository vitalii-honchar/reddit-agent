# Makefile for Reddit Agent project

.PHONY: help install dev-install test lint format clean regenerate-client start-api docker-build

# Default target
help:
	@echo "Available targets:"
	@echo "  install          - Install production dependencies"
	@echo "  dev-install      - Install development dependencies"
	@echo "  test             - Run tests"
	@echo "  lint             - Run linting"
	@echo "  format           - Format code"
	@echo "  clean            - Clean generated files"
	@echo "  regenerate-client - Regenerate OpenAPI client from running API"
	@echo "  start-api        - Start the FastAPI server"
	@echo "  docker-build     - Build and push Docker image"

# Install dependencies
install:
	uv sync

dev-install:
	uv sync --dev

# Testing
test:
	uv run pytest

test-integration:
	uv run pytest -m integration

# Code quality
lint:
	uv run ruff check .

format:
	uv run ruff check --fix .

# Clean generated files
clean:
	rm -rf src/insights/agentapi_client/
	rm -f openapi.json
	rm -f example_client_usage.py

# Start the FastAPI server in background
start-api:
	@echo "Starting FastAPI server..."
	uv run python -m src.agentapi.main &
	@echo "Waiting for server to start..."
	@sleep 3
	@echo "Server should be running on http://localhost:8000"

# Regenerate OpenAPI client
regenerate-client: start-api
	@echo "Fetching OpenAPI specification..."
	curl -s http://localhost:8000/openapi.json > openapi.json
	@echo "Removing old client..."
	rm -rf src/insights/agentapi_client/
	@echo "Generating new client..."
	uv run openapi-python-client generate --path openapi.json
	@echo "Moving client to proper location..."
	mv fast-api-client src/insights/agentapi_client
	@echo "Client regenerated successfully!"
	@echo "Stopping API server..."
	@pkill -f "python -m src.agentapi.main" || true
	@echo "Done!"

# Alternative: regenerate client with running server
regenerate-client-running:
	@echo "Fetching OpenAPI specification from running server..."
	curl -s http://localhost:8000/openapi.json > openapi.json
	@echo "Removing old client..."
	rm -rf src/insights/agentapi_client/
	@echo "Generating new client..."
	uv run openapi-python-client generate --path openapi.json
	@echo "Moving client to proper location..."
	mv fast-api-client src/insights/agentapi_client
	@echo "Client regenerated successfully!"

# Database operations
db-up:
	docker-compose up -d db

db-migrate:
	alembic revision --autogenerate -m "Auto migration"
	alembic upgrade head

# Docker
docker-build:
	docker buildx build --push --platform linux/arm64 --build-arg ARCH=linux/arm64 -t weaxme/pet-project:reddit-agent-latest .
