# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Python-based Reddit agent platform built with uv as the package manager. The project provides a multi-service architecture for creating, managing, and executing AI agents that scan Reddit for business opportunities. It features three main services: AgentAPI (backend API), Insights (web frontend), and Scheduler (background execution), all built with FastAPI and SQLModel/SQLAlchemy.

## Architecture

### Service Architecture
The project follows a microservices architecture with three main applications:

- **AgentAPI Service** (`src/agentapi/`) - REST API for agent configuration and execution management
- **Insights Service** (`src/insights/`) - Web-based frontend with dashboard and scheduling
- **Scheduler Service** (`src/scheduler/`) - Background service for automated agent execution

### Core Components

#### AgentAPI Service (`src/agentapi/`)
- **main.py** - FastAPI application with scheduler integration
- **routes/** - REST API endpoints for configurations and executions
- **schemas/** - Pydantic models for API request/response validation
- **dependencies.py** - Dependency injection container

#### Insights Service (`src/insights/`)
- **main.py** - FastAPI web application with Jinja2 templates
- **routes/insights.py** - Web interface routes
- **services/** - Business logic for agent configuration and API integration
- **agentapi_client/** - Auto-generated API client for AgentAPI service
- **templates/** - Jinja2 HTML templates

#### Scheduler Service (`src/scheduler/`)
- **scheduler.py** - Main scheduler manager with graceful shutdown
- **services/** - Agent execution and scheduling business logic
- **settings/** - Scheduler-specific configuration

#### Core Domain (`src/core/`)
- **models/** - SQLModel database entities
- **repositories/** - Data access layer
- **services/** - Domain business logic
- **scheduler/** - Shared scheduler components

#### Agents (`src/agents/`)
- **search_agent/** - Reddit search agent implementation
  - `search_agent.py` - LangGraph agent orchestration
  - `tool/reddit/` - Reddit API integration tools
  - `models.py` - Agent-specific data models
- **config/** - Agent configuration management
- **prompt/** - Prompt template management

### Key Architectural Patterns
- **Microservices**: Three independent FastAPI applications
- **Repository Pattern**: Data access abstraction in `src/core/repositories/`
- **Dependency Injection**: Service containers in each application
- **Auto-generated Clients**: OpenAPI client generation for inter-service communication
- **Background Processing**: Async scheduler with graceful shutdown
- **Database Migrations**: Alembic for schema versioning

## Development Commands

```bash
# Install dependencies
uv sync

# Database Setup
# Start PostgreSQL database (using Docker Compose)
docker-compose up -d db

# Run database migrations (after creating your models)
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head

# Running Services
# Run AgentAPI service (REST API backend)
uv run python -m src.agentapi.main

# Run Insights service (Web frontend)
uv run python -m src.insights.main

# Run Scheduler service (Background processing)
uv run python -m src.scheduler.scheduler

# Generate API Client (after AgentAPI changes)
# First start AgentAPI service, then:
uv run openapi-python-client generate --url http://localhost:8000/openapi.json --output-path src/insights/agentapi_client --config openapi-generator-config.yaml

# Testing
# Run all tests
uv run pytest

# Run specific test module
uv run pytest tests/test_agents/search_agent/test_search_agent.py -v

# Run specific test
uv run pytest tests/test_agents/search_agent/test_search_agent.py::TestSearchAgentIntegration::test_search_indie_project_marketing_opportunities -v

# Run integration tests only
uv run pytest -m integration

# Run tests in parallel
uv run pytest -n auto

# Code Quality
# Formatting and linting
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .
```

## Environment Setup

Create a `.env` file in the project root with these credentials:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit-agent:v0.1.0 (by /u/yourusername)
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://root:953810aa-684f-11f0-b390-5ee52574761b@localhost:5432/agentdb
ASYNC_DATABASE_URL=postgresql+asyncpg://root:953810aa-684f-11f0-b390-5ee52574761b@localhost:5432/agentdb
```

To get Reddit API credentials:
1. Go to https://www.reddit.com/prefs/apps
2. Create a new application (choose "script" type)
3. Use the client ID and secret in your .env file

## Service Details

### AgentAPI Service
- **Port**: Default 8000
- **Purpose**: RESTful API for managing agent configurations and executions
- **Database**: PostgreSQL with SQLModel/SQLAlchemy
- **Features**: Built-in scheduler manager, automatic database migrations
- **Key Endpoints**:
  - `/agent-configurations/` - CRUD operations for agent configs
  - `/agent-executions/` - CRUD operations for execution records

### Insights Service  
- **Port**: Default 8001
- **Purpose**: Web frontend for monitoring and managing agents
- **Features**: Jinja2 templates, static file serving, dashboard interface
- **API Integration**: Auto-generated client for AgentAPI service communication

### Scheduler Service
- **Purpose**: Background processing of pending agent executions
- **Features**: Configurable poll intervals, graceful shutdown, error handling
- **Architecture**: Event-driven with async processing loops

### Agent System
- **Search Agent**: LangGraph-based Reddit search with filtering strategies
- **Tools**: Reddit API integration with async PRAW
- **Configuration**: Flexible prompt and parameter management
- **Data Models**: Structured responses with Pydantic validation

## Package Management

This project uses `uv` for dependency management. The `uv.lock` file contains exact dependency versions.

- Add dependencies: `uv add <package>`
- Add dev dependencies: `uv add --dev <package>`
- Remove dependencies: `uv remove <package>`
- Update dependencies: `uv sync --upgrade`

## Development Best Practices

### Test Structure
- All tests must follow the **Given-When-Then** pattern with clear comments:
  - `# given` - Setup test data and preconditions
  - `# when` - Execute the action being tested  
  - `# then` - Verify the expected outcome
  - `# and` - Additional assertions (optional)

### Database Management
- Always generate new alembic migration and apply it after changes in SQL models

## Testing Practices
- **Database Testing Strategy**:
  - In test scenarios, do not mock the database
  - Use the same approach of database connection creation in a fixture like in `@tests/agentapi/conftest.py`