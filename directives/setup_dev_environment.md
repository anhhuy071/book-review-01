# Setup Dev Environment

## Goal
Get the Book Review Website running locally for development.

## Prerequisites
- Python 3.x installed
- Docker & Docker Compose installed (for PostgreSQL + pgAdmin)
- Git

## Steps

### 1. Clone & create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill in:
- `DATABASE_URL` — PostgreSQL connection string
- `FLASK_APP` — `application.py`
- `FLASK_ENV` — `development`

### 4. Start database services
```bash
docker-compose up -d
```

### 5. Initialize database
Run `tables.sql` against the PostgreSQL instance to create the schema.

### 6. Import book data
```bash
python import.py
```

### 7. Run the application
```bash
flask run
```

## Tools/Scripts
- `execution/` — (none yet, manual setup for now)
- `docker-compose.yml` — PostgreSQL + pgAdmin containers
- `import.py` — CSV book importer

## Edge Cases
- If port 5432 is already in use, update `docker-compose.yml` port mapping.
- If `.env` is missing, the app will crash on startup with a `KeyError`.
- On Windows, use `venv\Scripts\activate` instead of `source venv/bin/activate`.
