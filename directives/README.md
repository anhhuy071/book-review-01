# Directives

Directives are SOPs for repeatable Book Reviews Website tasks. They describe what to do, which scripts to run, expected outputs, and common failure modes.

## How To Use

1. Read the directive that matches the task.
2. Prefer existing deterministic scripts in `execution/` or root project scripts such as `import.py`.
3. Run commands with `uv` for host-side Python work.
4. Use Docker Compose for PostgreSQL, pgAdmin, and full-stack container checks.
5. If a task fails, fix the script or workflow, test it, then update the directive with the new learning.

## Current Directives

| Directive | Purpose |
|---|---|
| `setup_dev_environment.md` | Set up local Flask development with `uv` and Docker PostgreSQL |
| `import_books.md` | Import `books.csv` into the `books` table |
| `crawl_reviews.md` | Generate sample bot reviews with Google Books fallback data |

## Naming Convention

Use snake_case file names, for example `setup_dev_environment.md` or `import_books.md`.

## Expected Shape

Each directive should include:

- Goal
- Prerequisites
- Inputs
- Tools or scripts
- Steps
- Outputs
- Edge cases
