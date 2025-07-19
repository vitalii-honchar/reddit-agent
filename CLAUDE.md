# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Reddit agent project built with uv as the package manager. The project scans Reddit for business opportunities using PRAW (Python Reddit API Wrapper) and provides LangGraph-compatible tools for AI agents.

## Architecture

- **Entry point**: `src/reddit_agent/main.py` - Demonstrates Reddit tool functionality
- **Reddit Tool**: `src/reddit_agent/tool/reddit/` - Core Reddit scanning functionality
  - `service.py` - Business logic for Reddit API interactions
  - `tools.py` - LangGraph-compatible tool interfaces
  - `models.py` - Pydantic models for data structures
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

## Reddit API Setup

Create a `.env` file in the project root with your Reddit API credentials:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit-agent:v0.1.0 (by /u/yourusername)
```

To get Reddit API credentials:
1. Go to https://www.reddit.com/prefs/apps
2. Create a new application (choose "script" type)
3. Use the client ID and secret in your .env file

## Available Reddit Tools

The project provides 5 LangGraph-compatible tools:
- `scan_hot_posts` - Find hot posts in any subreddit
- `scan_rising_posts` - Find rising/trending posts
- `get_community_metrics` - Get subreddit statistics
- `analyze_post_comments` - Analyze comments on specific posts
- `scan_opportunities` - Comprehensive subreddit analysis

## Package Management

This project uses `uv` for dependency management. The `uv.lock` file contains exact dependency versions.

- Add dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Update dependencies: `uv sync --upgrade`