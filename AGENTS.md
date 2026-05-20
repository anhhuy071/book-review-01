# Agent Instructions

> This file is mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` so the same instructions load in any AI environment.

## Project Context

This is a Flask book review app backed by PostgreSQL. The normal development flow is:

- Run Python locally with `uv`.
- Run PostgreSQL/pgAdmin with `docker-compose.dev.yml`.
- Use `docker-compose.yml` for full-stack container checks.
- Keep deterministic task logic in scripts, and keep task instructions in directives.

## The 3-Layer Architecture

### Layer 1: Directive

- SOPs live in `directives/`.
- They define goals, inputs, tools/scripts, outputs, and edge cases.
- Read the relevant directive before doing repeatable project work.

### Layer 2: Orchestration

- This is the AI agent layer.
- Route the task, choose the right script, inspect errors, and decide the next step.
- Do not manually reimplement logic that already exists in `execution/` or root project scripts.

### Layer 3: Execution

- Deterministic scripts live in `execution/`.
- The current root importer is `import.py`.
- Scripts read configuration from `.env` and should be tested after changes.

## Operating Principles

1. Check existing tools first.
2. Prefer `uv run ...` for host-side Python commands.
3. Use `docker-compose.dev.yml` for local PostgreSQL/pgAdmin and `docker-compose.yml` for full-stack checks.
4. When something breaks, read the error, fix the tool or workflow, test it, then update the directive.
5. Do not commit secrets, local sessions, virtual environments, cache files, or `.tmp/` outputs.

## Important Project Files

- `application.py`: Flask app and routes
- `pyproject.toml`: Python project metadata and dependencies
- `uv.lock`: locked Python dependency graph
- `requirements.txt`: dependency export used by the current Dockerfile
- `docker-compose.dev.yml`: local PostgreSQL and pgAdmin services
- `docker-compose.yml`: full-stack container check
- `Dockerfile`: production-style web image
- `tables.sql`: database schema
- `books.csv`: seed book data
- `import.py`: imports books into PostgreSQL
- `execution/crawl_reviews.py`: inserts sample bot reviews
- `directives/`: SOPs for common project tasks
- `.tmp/`: regenerated intermediate files only

## Common Commands

Install dependencies:

```powershell
uv sync
```

Start the database:

```powershell
docker-compose -f docker-compose.dev.yml up -d
```

Import books:

```powershell
uv run python import.py
```

Run Flask locally:

```powershell
uv run flask --app application --debug run
```

Generate sample reviews:

```powershell
uv run python execution/crawl_reviews.py --limit 5
```

## Environment Notes

- For host-side Flask, `.env` should use `DB_HOST=localhost` and DB port `5432`.
- For the Docker web container, `.env` should use `DB_HOST=db`.
- `DATABASE_URL` is required by `application.py` and `import.py`.
- `flask_session/`, `__pycache__/`, `.venv/`, `.env`, and `.tmp/` should stay out of git.

## Summary

Be pragmatic and reliable: read the directive, use the script, test the result, and update the docs when the workflow changes.
