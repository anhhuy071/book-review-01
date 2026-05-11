import os
import csv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    """Import books from books.csv into the database (batch commit)."""
    with open("books.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row

        count = 0
        for isbn, title, author, year in reader:
            db.execute(
                text("INSERT INTO books (isbn, title, author, year) "
                     "VALUES (:isbn, :title, :author, :year)"),
                {"isbn": isbn, "title": title, "author": author, "year": year},
            )
            count += 1
            if count % 500 == 0:
                print(f"  … {count} books queued")

        db.commit()
        print(f"Done — {count} books imported successfully.")


if __name__ == "__main__":
    main()
