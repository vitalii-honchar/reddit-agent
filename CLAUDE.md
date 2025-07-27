# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Reddit agent project built with uv as the package manager. The project scans Reddit for business opportunities using async PRAW (Python Reddit API Wrapper) and provides LangGraph-compatible tools for AI agents. It features intelligent conversation summarization, multi-strategy filtering, and structured response generation.

## Architecture

### Core Components
- **Entry point**: `src/main.py` - Main application entry point
- **Search Agent**: `src/search_agent/search_agent.py` - LangGraph agent orchestration with conversation summarization
- **Reddit Tools**: `src/search_agent/tool/reddit/` - Async Reddit search implementation
  - `tools.py` - LangGraph-compatible tool interfaces with filtering strategies
  - `service.py` - Reddit API business logic
  - `models.py` - Pydantic data models for submissions and search queries
- **Hooks System**: `src/search_agent/hooks/` - Modular pre-processing hooks
  - `summarization.py` - LLM-powered conversation summarization with failsafe
- **Configuration**: `src/config/` - Centralized configuration management
- **Prompts**: `prompts/` - Template-based prompt system for agent behavior

### Key Architectural Patterns
- **Strategy Pattern**: Multi-layer filtering system with `SubmissionFilterStrategy` implementations
- **Dependency Injection**: LLM and configuration dependencies injected into hooks and services
- **Async/Await**: Full async support throughout Reddit API interactions
- **Structured Responses**: Pydantic models ensure type safety and validation

## Development Commands

```bash
# Install dependencies
uv sync

# Run the application  
uv run python src/main.py

# Run the FastAPI server
uv run python -m src.api.main

# Start PostgreSQL database (using Docker Compose)
docker-compose up -d db

# Run database migrations (after creating your models)
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_search_agent.py::TestSearchAgentIntegration::test_search_indie_project_marketing_opportunities -v

# Run integration tests only
uv run pytest -m integration

# Code formatting and linting
uv run ruff check .
uv run ruff check --fix .
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

## Advanced Features

### Conversation Summarization
- **Location**: `src/search_agent/hooks/summarization.py`
- **Behavior**: Automatically summarizes conversations when token limits are exceeded
- **Failsafe**: Returns original messages if LLM summarization fails (preserves data)
- **Prompt**: `prompts/summarization/system.md`

### Multi-Strategy Filtering
- **Pattern**: Strategy pattern with `SubmissionFilterStrategy` base class
- **Filters**: Score, age, content length, keywords, flairs, comments quality
- **Configuration**: Comprehensive filtering options in `SearchQuery` model

### Structured Data Models
- **SearchResult**: Top-level response with findings and metadata
- **Finding**: Individual insights with action items and relevance scoring
- **RedditSubmission**: Structured post data with top comments
- **SearchQuery**: Reddit search parameters with filtering configuration

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