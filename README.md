# 📚 Book Reviews Website

A Flask web application that lets users search 5,000 books, leave reviews, and read reviews from others. Book ratings from [Goodreads](https://www.goodreads.com) are also displayed on each book's page.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Registration & Login | Secure user authentication with session management |
| 🔍 Search | Search books by title, author, or ISBN (partial match supported) |
| 📖 Book Page | View book details, publication year, ISBN, and user reviews |
| ⭐ Review Submission | Rate books from 1–5 stars and leave a written review (one per book per user) |
| 🌐 Goodreads Integration | Displays Goodreads average rating and total ratings count |
| 🔌 REST API | Query book details programmatically via `/api/<isbn>` |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** PostgreSQL
- **Frontend:** Jinja2 templates
- **Deployment:** Docker, Gunicorn

---

## 🚀 Installation

### Option 1: Docker (Recommended)

The easiest way to run the project. Only requires [Docker Desktop](https://www.docker.com/products/docker-desktop).

**1. Clone the repository:**
```bash
git clone <your-repo-url>
cd Book-review-website
```

**2. Copy and configure your environment file:**
```bash
cp .env.example .env
```
Edit `.env` with your preferred credentials (passwords, etc.).

**3. Start all services (Web App + Database + pgAdmin):**
```bash
docker-compose up -d --build
```
> The database tables are created automatically on the first run via `tables.sql`.

**4. Import 5,000 books into the database:**
```bash
docker-compose exec web python import.py
```

**5. Access the app:**
- 🌐 Web App: `http://localhost:5000`
- 🗄️ pgAdmin (DB GUI): `http://localhost:5050`
  - Email: `admin@admin.com` | Password: `admin`
  - Connect to server: host `db`, port `5432`, user `postgres`

---

### Option 2: Local Development (Flask + Docker DB)

Run Flask locally while the database runs in Docker.

**1. Install dependencies** (using `uv` or `pip`):
```bash
pip install -r requirements.txt
```

**2. Configure `.env`:**
```bash
cp .env.example .env
```
Make sure `DB_HOST=localhost` in your `.env` file.

**3. Start only the database container:**
```bash
docker-compose up -d db
```

**4. Import books:**
```bash
python import.py
```

**5. Run the Flask development server:**
```bash
flask run
```

Access the app at `http://localhost:5000`.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env` to git.**

| Variable | Description | Default |
|---|---|---|
| `FLASK_APP` | Flask app entry point | `application.py` |
| `FLASK_DEBUG` | Enable debug mode | `1` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | *(set your own)* |
| `DB_NAME` | Database name | `book_review` |
| `DB_HOST` | DB host (`localhost` for local, `db` for Docker) | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DATABASE_URL` | Full connection string (auto-built from above) | — |
| `PGADMIN_EMAIL` | pgAdmin login email | `admin@admin.com` |
| `PGADMIN_PASSWORD` | pgAdmin login password | *(set your own)* |

---

## 🔌 REST API

### `GET /api/<isbn>`

Returns book details and review stats for a given 10-digit ISBN.

**Example response:**
```json
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
```

---

## 🗃️ Database Schema

The database consists of three tables:
- **Users** – stores registered user accounts
- **Books** – stores 5,000 books (imported from `books.csv`)
- **Reviews** – stores user reviews linked to users and books

See `tables.sql` for the full schema, and `db-schema.png` for a visual diagram.
