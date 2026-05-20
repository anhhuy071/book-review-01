import os
import sys
import random
import time
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Fallback to localhost if connecting from the host machine rather than a container
db_url = os.getenv("DATABASE_URL")
if db_url and "@db:" in db_url:
    db_url = db_url.replace("@db:", "@localhost:")
elif not db_url:
    db_user = os.getenv("DB_USER", "postgres")
    db_pwd = os.getenv("DB_PASSWORD", "your_strong_password_here")
    db_name = os.getenv("DB_NAME", "book_review")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    
    # If the script is running outside docker, we should use localhost instead of 'db'
    if db_host == "db":
        db_host = "localhost"
        
    db_url = f"postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)

BOT_EMAIL = "bot@bookreviews.local"
BOT_FIRSTNAME = "Review"
BOT_LASTNAME = "Bot"
BOT_PASSWORD = "botpassword123"

def ensure_bot_user(conn):
    """Ensure the bot user exists and return its user_id."""
    user = conn.execute(text("SELECT userid FROM users WHERE email = :email"), {"email": BOT_EMAIL}).fetchone()
    if user:
        return user[0]
    
    print("Creating Bot User...")
    from werkzeug.security import generate_password_hash
    conn.execute(
        text("INSERT INTO users (firstname, lastname, email, password) VALUES (:fname, :lname, :email, :pwd)"),
        {
            "fname": BOT_FIRSTNAME,
            "lname": BOT_LASTNAME,
            "email": BOT_EMAIL,
            "pwd": generate_password_hash(BOT_PASSWORD)
        }
    )
    conn.commit()
    
    user = conn.execute(text("SELECT userid FROM users WHERE email = :email"), {"email": BOT_EMAIL}).fetchone()
    return user[0]

def fetch_review(isbn, title):
    """Fetch a review from Google Books API as a fallback since Goodreads scraping is unstable."""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            volume_info = data["items"][0].get("volumeInfo", {})
            search_info = data["items"][0].get("searchInfo", {})
            
            description = volume_info.get("description", "")
            snippet = search_info.get("textSnippet", "")
            
            if snippet:
                # Clean HTML tags from snippet
                import re
                clean_snippet = re.sub('<[^<]+>', '', snippet)
                return clean_snippet, random.randint(3, 5)
            elif description:
                # Take first 2 sentences of description as a review
                sentences = description.split(". ")
                short_desc = ". ".join(sentences[:2]) + "."
                return f"An interesting read: {short_desc}", random.randint(3, 5)
                
    except Exception as e:
        print(f"Error fetching data for ISBN {isbn}: {e}")
        
    # Fallback to generic reviews if API fails
    generic_reviews = [
        f"I really enjoyed reading {title}. The pacing was great and the characters felt alive.",
        f"{title} is a solid book. It kept me hooked until the very end. Highly recommended!",
        f"A decent read, though some parts of {title} dragged a bit. Still worth checking out.",
        f"Absolutely fantastic! I couldn't put {title} down. One of the best books I've read this year."
    ]
    return random.choice(generic_reviews), random.randint(3, 5)

def crawl_and_insert_reviews(limit=5):
    """Main execution function."""
    print(f"Starting review crawler (limit: {limit} books)...")
    
    with engine.connect() as conn:
        bot_user_id = ensure_bot_user(conn)
        print(f"Bot User ID: {bot_user_id}")
        
        # Get books that the bot hasn't reviewed yet
        books = conn.execute(
            text("""
                SELECT b.bookid, b.isbn, b.title 
                FROM books b 
                LEFT JOIN reviews r ON b.bookid = r.book_id AND r.user_id = :bot_id
                WHERE r.reviewid IS NULL
                LIMIT :limit
            """),
            {"bot_id": bot_user_id, "limit": limit}
        ).fetchall()
        
        if not books:
            print("No new books to review. Exiting.")
            return
            
        print(f"Found {len(books)} books to review.")
        
        for book in books:
            print(f"Processing '{book.title}' (ISBN: {book.isbn})...")
            
            # Simulate human-like delay
            time.sleep(random.uniform(1.0, 2.5))
            
            review_text, rating = fetch_review(book.isbn, book.title)
            
            print(f"-> Generated Rating: {rating}")
            print(f"-> Generated Comment: {review_text[:50]}...")
            
            try:
                conn.execute(
                    text("""
                        INSERT INTO reviews (user_id, book_id, rating, comment)
                        VALUES (:uid, :bid, :rating, :comment)
                    """),
                    {
                        "uid": bot_user_id,
                        "bid": book.bookid,
                        "rating": rating,
                        "comment": review_text
                    }
                )
                conn.commit()
                print("-> Success!")
            except Exception as e:
                conn.rollback()
                print(f"-> Error inserting review: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Crawl and insert book reviews.")
    parser.add_argument("--limit", type=int, default=5, help="Number of books to process")
    args = parser.parse_args()
    
    crawl_and_insert_reviews(limit=args.limit)
