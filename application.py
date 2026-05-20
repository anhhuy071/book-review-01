import os
import requests

from flask import Flask, session, render_template, redirect, request, url_for, jsonify, flash
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect(app)

# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-fallback-change-in-production")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# --------------------------------------------------------------------------- #
#  Database
# --------------------------------------------------------------------------- #

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is None:
            flash("Please log in to access this function.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def fetch_openlib_data(isbn):
    """Fetch book cover, ratings, and description from OpenLibrary.

    Returns a dict with graceful fallbacks — never raises.
    """
    result = {
        "cover": None,
        "rating_average": None,
        "rating_count": 0,
        "description": None,
    }

    try:
        # --- Cover image ---
        data_resp = requests.get(
            f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json",
            timeout=5,
        )
        data_resp.raise_for_status()
        data = data_resp.json()
        book_key = f"ISBN:{isbn}"

        if book_key not in data:
            return result

        book_data = data[book_key]
        if "cover" in book_data:
            result["cover"] = book_data["cover"].get("medium") or book_data["cover"].get("small")

        # --- Works key (needed for ratings + description) ---
        details_resp = requests.get(
            f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json",
            timeout=5,
        )
        details_resp.raise_for_status()
        details_data = details_resp.json()

        if book_key not in details_data:
            return result

        works = details_data[book_key].get("details", {}).get("works", [])
        if not works:
            return result

        work_key = works[0].get("key", "")

        # --- Ratings ---
        try:
            ratings_resp = requests.get(
                f"https://openlibrary.org{work_key}/ratings.json",
                timeout=5,
            )
            ratings_resp.raise_for_status()
            summary = ratings_resp.json().get("summary", {})
            result["rating_average"] = summary.get("average")
            result["rating_count"] = summary.get("count", 0)
        except Exception as e:
            app.logger.warning(f"Failed to fetch ratings for ISBN {isbn}: {e}")

        # --- Description ---
        try:
            work_resp = requests.get(
                f"https://openlibrary.org{work_key}.json",
                timeout=5,
            )
            work_resp.raise_for_status()
            desc = work_resp.json().get("description")
            if isinstance(desc, dict):
                result["description"] = desc.get("value")
            elif isinstance(desc, str):
                result["description"] = desc
        except Exception as e:
            app.logger.warning(f"Failed to fetch description for ISBN {isbn}: {e}")

    except Exception as e:
        app.logger.error(f"OpenLibrary API error for ISBN {isbn}: {e}")

    return result


# --------------------------------------------------------------------------- #
#  Routes
# --------------------------------------------------------------------------- #

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # --- Validation ---
    first_name = request.form.get("first_name", "").strip()
    last_name  = request.form.get("last_name", "").strip()
    email      = request.form.get("email", "").strip()
    password1  = request.form.get("password1", "")
    password2  = request.form.get("password2", "")

    if not first_name:
        flash("First name is required.", "error")
        return redirect(url_for("register"))
    if not last_name:
        flash("Last name is required.", "error")
        return redirect(url_for("register"))
    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("register"))
    if not password1 or not password2:
        flash("Password is required.", "error")
        return redirect(url_for("register"))
    if password1 != password2:
        flash("Passwords do not match.", "error")
        return redirect(url_for("register"))

    # --- Insert user ---
    try:
        db.execute(
            text("INSERT INTO users (firstname, lastname, email, password) "
                 "VALUES (:firstname, :lastname, :email, :password)"),
            {
                "firstname": first_name,
                "lastname": last_name,
                "email": email,
                "password": generate_password_hash(password1),
            },
        )
        db.commit()
    except Exception as e:
        db.rollback()
        app.logger.error(f"Registration error: {e}")
        flash("Registration failed. This email might already be registered.", "error")
        return redirect(url_for("register"))

    # --- Auto-login ---
    user = db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email},
    ).fetchone()

    session["user_id"]  = user.userid
    session["email"]    = user.email
    session["firstname"] = user.firstname
    session["logged_in"] = True

    flash(f"Welcome, {user.firstname}! Your account has been created.", "success")
    return redirect(url_for("search"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # --- Validation ---
    form_email    = request.form.get("email", "").strip()
    form_password = request.form.get("password", "")

    if not form_email:
        flash("Email is required.", "error")
        return redirect(url_for("login"))
    if not form_password:
        flash("Password is required.", "error")
        return redirect(url_for("login"))

    # --- Authenticate ---
    try:
        user = db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": form_email},
        ).fetchone()
    except Exception as e:
        app.logger.error(f"Login query error: {e}")
        flash("A database error occurred. Please try again later.", "error")
        return redirect(url_for("login"))

    if user is None:
        flash("No account found with that email.", "error")
        return redirect(url_for("login"))

    if not check_password_hash(user.password, form_password):
        flash("Invalid password.", "error")
        return redirect(url_for("login"))

    # --- Set session (clear first to rotate session id) ---
    session.clear()
    session["user_id"]  = user.userid
    session["email"]    = user.email
    session["firstname"] = user.firstname
    session["logged_in"] = True

    return redirect(url_for("search"))


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    query = request.form.get("input-search", "").strip()
    if not query:
        flash("Search field cannot be empty.", "error")
        return redirect(url_for("search"))

    try:
        result = db.execute(
            text("SELECT * FROM books WHERE LOWER(isbn) LIKE :query "
                 "OR LOWER(title) LIKE :query OR LOWER(author) LIKE :query"),
            {"query": f"%{query.lower()}%"},
        ).fetchall()
    except Exception as e:
        app.logger.error(f"Search error: {e}")
        flash("An error occurred while searching. Please try again.", "error")
        return redirect(url_for("search"))

    if not result:
        flash("No books found matching your search.", "warning")
        return redirect(url_for("search"))

    return render_template("list.html", result=result)


@app.route("/details/<int:bookid>", methods=["GET", "POST"])
def details(bookid):
    if request.method == "GET":
        # --- Fetch book ---
        result = db.execute(
            text("SELECT * FROM books WHERE bookid = :bookid"),
            {"bookid": bookid},
        ).fetchone()

        if not result:
            flash("Book not found.", "error")
            return redirect(url_for("search"))

        # --- External data (resilient) ---
        openlib = fetch_openlib_data(result.isbn)

        # --- Reviews ---
        comment_list = db.execute(
            text("SELECT u.firstname, u.lastname, r.rating, r.comment "
                 "FROM reviews r JOIN users u ON u.userid = r.user_id "
                 "WHERE book_id = :id"),
            {"id": bookid},
        ).fetchall()

        return render_template(
            "details.html",
            result=result,
            comment_list=comment_list,
            bookid=bookid,
            openlib={
                "average": openlib["rating_average"],
                "count":   openlib["rating_count"],
            },
            cover=openlib["cover"],
            descriptions=openlib["description"],
        )

    # --- POST: submit review ---
    if "user_id" not in session:
        flash("Please log in to submit a review.", "warning")
        return redirect(url_for("login"))

    already = db.execute(
        text("SELECT 1 FROM reviews WHERE user_id = :uid AND book_id = :bid"),
        {"uid": session["user_id"], "bid": bookid},
    ).fetchone()

    if already:
        flash("You have already reviewed this book.", "warning")
        return redirect(url_for("details", bookid=bookid))

    user_comment = request.form.get("comments", "").strip()
    user_rating  = request.form.get("rating")

    if not user_comment:
        flash("Review comment cannot be empty.", "error")
        return redirect(url_for("details", bookid=bookid))

    try:
        db.execute(
            text("INSERT INTO reviews (user_id, book_id, rating, comment) "
                 "VALUES (:user_id, :book_id, :rating, :comment)"),
            {
                "user_id": session["user_id"],
                "book_id": bookid,
                "rating": user_rating,
                "comment": user_comment,
            },
        )
        db.commit()
    except Exception as e:
        db.rollback()
        app.logger.error(f"Review submission error: {e}")
        flash("Failed to submit your review. Please try again.", "error")
        return redirect(url_for("details", bookid=bookid))

    flash("Your review has been posted!", "success")
    return redirect(url_for("details", bookid=bookid))


# --------------------------------------------------------------------------- #
#  API
# --------------------------------------------------------------------------- #

@app.route("/api/<string:isbn>")
@csrf.exempt
# @login_required
def api(isbn):
    try:
        book = db.execute(
            text("SELECT * FROM books WHERE isbn = :isbn"),
            {"isbn": isbn},
        ).fetchone()
    except Exception as e:
        app.logger.error(f"API query error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    if book is None:
        return jsonify({"error": "Not Found"}), 404

    openlib = fetch_openlib_data(isbn)

    return jsonify({
        "title":   book.title,
        "author":  book.author,
        "year":    book.year,
        "isbn":    book.isbn,
        "average": openlib["rating_average"],
        "count":   openlib["rating_count"],
    })


# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")