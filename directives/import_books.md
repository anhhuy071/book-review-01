# Import Books From CSV

## Goal

Populate the `books` table with the 5,000 records from `books.csv`.

## Prerequisites

- PostgreSQL is running.
- `tables.sql` has created the `books` table.
- `.env` contains a valid `DATABASE_URL`.
- Python dependencies are installed with `uv sync`.

## Inputs

- `books.csv`: CSV source with `isbn`, `title`, `author`, and `year`
- `.env`: database connection settings
- `tables.sql`: expected database schema

## Tools/Scripts

- `import.py`: root-level importer that inserts CSV rows into PostgreSQL with SQLAlchemy

## Steps

### Host-side Flask/dev database

```powershell
docker-compose -f docker-compose.dev.yml up -d
uv run python import.py
```

### Full Docker stack

```powershell
docker-compose up -d --build
docker-compose exec web python import.py
```

## Outputs

- The `books` table is populated from `books.csv`.
- The script prints progress every 500 rows and a final imported count.

## Edge Cases

- `DATABASE_URL` is required. The script stops immediately if it is missing.
- `books.isbn` is unique. Running the importer again against the same database can fail on duplicate ISBNs.
- If the `books` table does not exist, start with a fresh Docker volume or apply `tables.sql` manually.
- If `.env` uses `DB_HOST=db`, run the importer inside the Docker web container. For host-side `uv run`, use `DB_HOST=localhost`.
