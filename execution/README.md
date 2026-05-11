# Execution Scripts

Deterministic Python scripts that handle the actual work for the Book Review Website.

## Principles

- Each script does **one thing well**
- All scripts are **well-commented** and **testable**
- Environment variables and secrets come from `.env`
- Scripts should handle errors gracefully and return clear exit codes

## Naming Convention

Use snake_case: `import_books.py`, `setup_db.py`, `seed_data.py`
