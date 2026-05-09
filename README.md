# Book Reviews
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Overview

This web site features 5000 hand picked books allowing users to search, leave reviews for individual books, and see the reviews made by other people. It also uses a third-party API by Goodreads.com, another book review website, to pull ratings from a broader audience. In addition, users are able to query for book details and book reviews programmatically via website's API. 

# Installation

## Installation via Docker (Recommended)
This project is fully containerized. You only need [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your machine.

1. Clone the repository and navigate into the project directory.
2. Open your terminal and run the following command to start both the Web App and the Database:
   ```bash
   docker compose up -d --build
   ```
   *(Note: The database tables will be automatically created on the first run).*
3. To populate the database with 5000 books from `books.csv`, run:
   ```bash
   docker compose exec web python import.py
   ```
4. Access the web application at `http://localhost:5000`.

## Manual Installation (Legacy)
If you prefer not to use Docker, ensure you have PostgreSQL and Python installed:
1. Run `uv pip install -r requirements.txt` (or `pip install -r requirements.txt`).
2. Set the environment variables in a `.env` file or export them (`FLASK_APP=application.py`, `DATABASE_URL=...`).
3. Run `tables.sql` against your database manually.
4. Run `python import.py` to import books.
5. Execute `flask run` to start the server.

# Features of the applications

* *Registration*: Users are be able to register.
* *Login*: Users, once registered, should be able to log in to the website with their username and password.
* *Logout*: Logged in users should be able to log out of the site.
* *Search*: Once a user has logged in, they are taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the website displays a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, search page should find matches for those as well!
* *Book Page*: When users click on a book details from the results of the search page, they are taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on the website.
* *Review Submission*: On the book page, users are be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users won't be able to submit multiple reviews for the same book.
* *Goodreads Review Data*: On the book details page, users are able to see the average rating and number of ratings the work has received from Goodreads.

# API Access

Book Reviews API allows developers access to Book Reviews data in order to help other websites or applications that deal with books be more personalized, social and engaging.

## API methods

`/api/<isbn>` - where `<isbn>` is a 10 digit ISBN number. This GET request returns a JSON response containing the book's title, author, publication date, ISBN number, review count, and average score. Example format:
``` json
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
```
