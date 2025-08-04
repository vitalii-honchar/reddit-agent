# Reddit Agent Platform

📝 **[Read the project article: Designing AI Applications: Principles of Distributed Systems](https://vitaliihonchar.com/insights/designing-ai-applications-principles-of-distributed-systems)**

A comprehensive Python-based Reddit agent platform for discovering business opportunities through automated Reddit scanning and analysis.

## Architecture Overview

The platform follows a microservices architecture with three main services:

- **AgentAPI Service** - REST API for agent configuration and execution management
- **Insights Service** - Web-based frontend with dashboard and scheduling interface  
- **Scheduler Service** - Background service for automated agent execution

## Features

- 🤖 **LangGraph-powered search agents** for intelligent Reddit content analysis
- 🌐 **Web dashboard** for monitoring and managing agent configurations
- ⚡ **Background scheduling** with configurable execution intervals
- 🔗 **Auto-generated API clients** for seamless inter-service communication
- 🗄️ **PostgreSQL database** with SQLModel/SQLAlchemy ORM
- 🧪 **Comprehensive testing** with pytest and async support

## Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL database
- Reddit API credentials
- OpenAI API key

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd reddit-agent
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=reddit-agent:v0.1.0 (by /u/yourusername)
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://root:953810aa-684f-11f0-b390-5ee52574761b@localhost:5432/agentdb
   ASYNC_DATABASE_URL=postgresql+asyncpg://root:953810aa-684f-11f0-b390-5ee52574761b@localhost:5432/agentdb
   ```

4. **Start the database**
   ```bash
   docker-compose up -d db
   ```

5. **Run database migrations**
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

### Running Services

**AgentAPI Service (Port 8000)**
```bash
uv run python -m src.agentapi.main
```

**Insights Service (Port 8001)**
```bash
uv run python -m src.insights.main
```

**Scheduler Service**
```bash
uv run python -m src.scheduler.scheduler
```

## Development

### Testing

Run all tests:
```bash
uv run pytest -v
```

Run specific test modules:
```bash
uv run pytest tests/test_agents/search_agent/test_search_agent.py -v
```

Run integration tests only:
```bash
uv run pytest -m integration
```

Run tests in parallel:
```bash
uv run pytest -n auto
```

### Code Quality

Format and lint code:
```bash
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .
```

### API Client Generation

After making changes to AgentAPI, regenerate the client for Insights service:

1. Start AgentAPI service
2. Generate new client:
   ```bash
   uv run openapi-python-client generate --url http://localhost:8000/openapi.json --output-path src/insights/agentapi_client --config openapi-generator-config.yaml
   ```

## Project Structure

```
src/
├── agentapi/          # REST API service
│   ├── routes/        # API endpoints
│   └── schemas/       # Pydantic models
├── insights/          # Web frontend service
│   ├── routes/        # Web interface routes
│   ├── services/      # Business logic
│   ├── templates/     # Jinja2 templates
│   └── agentapi_client/ # Auto-generated API client
├── scheduler/         # Background execution service
│   ├── services/      # Scheduler business logic
│   └── settings/      # Configuration
├── core/              # Shared domain logic
│   ├── models/        # SQLModel entities
│   ├── repositories/ # Data access layer
│   └── services/      # Domain services
└── agents/            # Agent implementations
    ├── search_agent/  # Reddit search agent
    ├── config/        # Configuration management
    └── prompt/        # Prompt templates
```

## Getting Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Create a new application (choose "script" type)
3. Use the client ID and secret in your `.env` file

## Database Migrations

Create new migration after model changes:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Contributing

1. Follow the **Given-When-Then** pattern for all tests
2. Always generate and apply database migrations after model changes
3. Use `uv` for dependency management
4. Run code quality checks before committing

## License

[Add your license information here]