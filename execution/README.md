# Execution Scripts

Execution scripts are deterministic tools used by directives. Keep repeatable logic here instead of doing multi-step data work manually.

## Current Scripts

| Script | Purpose |
|---|---|
| `crawl_reviews.py` | Creates a bot user and inserts sample reviews for imported books |

The book importer currently lives at the project root as `import.py` because the original app expects `books.csv` beside it.

## Run Commands

From the project root:

```powershell
uv run python execution/crawl_reviews.py --limit 5
```

Root importer:

```powershell
uv run python import.py
```

## Principles

- Scripts should read secrets and connection settings from `.env`.
- Scripts should fail clearly when required environment variables are missing.
- Scripts should be safe to run in small batches first.
- Update the matching directive whenever script behavior, arguments, or edge cases change.

## Naming Convention

Use snake_case names such as `crawl_reviews.py` or `seed_reviews.py`.
