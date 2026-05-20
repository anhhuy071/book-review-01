# Setup Dev Environment

## Goal

Run the Book Reviews Website locally with Flask on the host machine and PostgreSQL in Docker.

## Prerequisites

- Python 3.12 or compatible Python 3.x
- `uv`
- Docker Desktop or Docker Engine with Docker Compose
- Git

## Inputs

- `.env.example`
- `pyproject.toml`
- `uv.lock`
- `docker-compose.dev.yml`
- `tables.sql`
- `books.csv`

## Tools/Scripts

- `uv` for virtual environment and dependency management
- `docker-compose.dev.yml` for local PostgreSQL and pgAdmin
- `import.py` for importing book data

## Steps

### 1. Create the Python environment

```powershell
uv sync
```

### 2. Configure environment variables

```powershell
Copy-Item .env.example .env
```

For host-side Flask with Docker PostgreSQL, `.env` should use localhost:

```env
FLASK_APP=application
FLASK_DEBUG=1
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review
```

### 3. Start PostgreSQL

```powershell
docker-compose -f docker-compose.dev.yml up -d
```

`tables.sql` runs automatically when the PostgreSQL volume is created for the first time.

### 4. Import book data

```powershell
uv run python import.py
```

### 5. Run Flask

```powershell
uv run flask --app application --debug run
```

Open `http://localhost:5000`.

## Optional Full-Stack Docker Check

Use this when checking the containerized app:

```powershell
docker-compose up -d --build
docker-compose exec web python import.py
```

For this mode, `.env` must use the Docker service name:

```env
DB_HOST=db
DATABASE_URL=postgresql://postgres:postgres@db:5432/book_review
```

## Outputs

- Flask app available at `http://localhost:5000`
- PostgreSQL running on host port `5432`
- pgAdmin available at `http://localhost:5050` if started
- `books` table populated after running `import.py`

## Edge Cases

- If `DATABASE_URL` is missing, `application.py` and `import.py` raise `RuntimeError`.
- If port `5432` is already in use, change the PostgreSQL port mapping in `docker-compose.dev.yml` and update `DATABASE_URL`.
- If `DB_HOST=db` is used while Flask runs on the host, the app cannot reach the database. Use `localhost` for host-side Flask.
- If `import.py` is run twice, the `books.isbn` unique constraint can fail. Reset the DB volume or make the importer idempotent before repeated imports.
- If the database volume already exists, changes to `tables.sql` will not rerun automatically. Recreate the local dev volume with `docker-compose -f docker-compose.dev.yml down -v`.
