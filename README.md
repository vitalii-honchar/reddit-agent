# Agent API

## Migrations
1. Crete Alembic revision: `alembic revision --autogenerate -m "Init revision"`
2. Run migrations: `alembic upgrade head`

## Tests

```bash
uv run pytest -v
```
## Code Style

```bash
uv run ruff check --fix
```