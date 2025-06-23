# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Reddit agent project built with uv as the package manager. The project is in early development stage with a minimal structure.

## Architecture

- **Entry point**: `src/reddit_agent/main.py` - Contains the main function that currently prints a hello message
- **Package structure**: Standard Python package layout under `src/reddit_agent/`
- **Dependencies**: Managed via `pyproject.toml` with uv as the package manager

## Development Commands

```bash
# Install dependencies and set up environment
uv sync

# Run the application
uv run python -m reddit_agent.main

# Alternative run method
uv run python src/reddit_agent/main.py
```

## Package Management

This project uses `uv` for dependency management. The `uv.lock` file contains exact dependency versions.

- Add dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Update dependencies: `uv sync --upgrade`