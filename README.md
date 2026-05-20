# Book Reviews Website

A Flask web application for searching books, creating user accounts, posting one review per book, and viewing book metadata from OpenLibrary.

## Features

| Feature | Description |
|---|---|
| Registration and login | User accounts with hashed passwords and server-side sessions |
| Book search | Search by title, author, or ISBN with partial matches |
| Book detail pages | View local book data, reviews, OpenLibrary cover, rating summary, and description |
| Review submission | Authenticated users can rate books from 1 to 5 and leave a comment |
| REST API | Query book details and OpenLibrary rating data with `/api/<isbn>` |
| Seed data | Import 5,000 books from `books.csv` |
| Review crawler | Generate sample bot reviews with `execution/crawl_reviews.py` |

## Tech Stack

- Python 3.12
- Flask, Flask-Session, Flask-WTF
- SQLAlchemy with PostgreSQL
- Jinja2 templates
- Docker Compose for local PostgreSQL/pgAdmin and optional full-stack runs
- Gunicorn for containerized web serving
- `uv` with `pyproject.toml` and `uv.lock` for local Python dependency management
- `requirements.txt` for the current Docker image install step

## Recommended Local Development

Run Flask locally from PowerShell with `uv`, and run only PostgreSQL/pgAdmin in Docker.

### 1. Install uv

```powershell
pip install uv
```

### 2. Sync the Python environment

```powershell
uv sync
```

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

For local Flask plus Docker DB, make sure `.env` points to localhost:

```env
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/book_review
FLASK_APP=application
FLASK_DEBUG=1
```

### 4. Start PostgreSQL

```powershell
docker-compose -f docker-compose.dev.yml up -d
```

The database schema is initialized from `tables.sql` when the database volume is created for the first time.

### 5. Import books

```powershell
uv run python import.py
```

### 6. Run Flask with hot reload

```powershell
uv run flask run
```

`FLASK_APP=application` and `FLASK_DEBUG=1` from `.env` make the shorter command work.

Open `http://localhost:5000`.

## Full Docker Run

Use this when you want the web app, PostgreSQL, and pgAdmin running together in containers.

Stop the dev stack first if it is already running:

```powershell
docker-compose -f docker-compose.dev.yml down
```

For the Docker web container, `.env` should use the Docker service hostname:

```env
DB_HOST=db
DATABASE_URL=postgresql://postgres:postgres@db:5432/book_review
```

Start everything:

```powershell
docker-compose up -d --build
```

Import books inside the web container:

```powershell
docker-compose exec web python import.py
```

Access:

- Web app: `http://localhost:5000`
- pgAdmin: `http://localhost:5050`
- pgAdmin database host: `db`
- PostgreSQL port inside Docker: `5432`

## Switching Docker Workflows

Use only one Compose workflow at a time because both files publish PostgreSQL on `5432` and pgAdmin on `5050`.

Switch from full Docker back to local Flask development:

```powershell
docker-compose down
docker-compose -f docker-compose.dev.yml up -d
uv run flask run
```

Stop everything from both workflows:

```powershell
docker-compose down
docker-compose -f docker-compose.dev.yml down
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your local values. Never commit `.env`.

| Variable | Description |
|---|---|
| `FLASK_APP` | Flask entry point. Use `application` or `application.py` |
| `FLASK_DEBUG` | Enables Flask debug mode when set to `1` |
| `SECRET_KEY` | Flask session and CSRF secret |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_NAME` | PostgreSQL database name |
| `DB_HOST` | `localhost` for host-side Flask, `db` for Docker web |
| `DB_PORT` | PostgreSQL port |
| `DATABASE_URL` | SQLAlchemy connection string used by the app and scripts |
| `PGADMIN_EMAIL` | pgAdmin login email |
| `PGADMIN_PASSWORD` | pgAdmin login password |

## Useful Commands

Import book data:

```powershell
uv run python import.py
```

Generate sample bot reviews:

```powershell
uv run python execution/crawl_reviews.py --limit 5
```

Stop Docker services:

```powershell
docker-compose down
docker-compose -f docker-compose.dev.yml down
```

Reset the local Docker database volume:

```powershell
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
uv run python import.py
```

## REST API

### `GET /api/<isbn>`

Returns local book details plus OpenLibrary rating summary.

Example:

```json
{
  "title": "Memory",
  "author": "Doug Lloyd",
  "year": 2015,
  "isbn": "1632168146",
  "average": 4.0,
  "count": 123
}
```

If the ISBN is missing, the API returns:

```json
{
  "error": "Not Found"
}
```

## Database Schema

The database has three tables:

- `users`: registered user accounts
- `books`: imported records from `books.csv`
- `reviews`: user and bot reviews linked to books

See `tables.sql` for the SQL schema and `db-schema.png` for the visual diagram.

## Project Workflow

This repo uses a small directive/execution workflow:

- `directives/`: Markdown SOPs for common tasks
- `execution/`: deterministic Python scripts for repeatable jobs
- `.tmp/`: regenerated intermediate files only

Before adding a new script, check `execution/` and the relevant directive first.
