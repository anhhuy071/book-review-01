# Crawl Reviews Directive

**Goal:** Automatically crawl or generate book reviews and insert them into the `Reviews` table to populate the application with realistic data.

## Execution Context

- **Script:** `execution/crawl_reviews.py`
- **Dependencies:** `requests`, `sqlalchemy`, `dotenv`, `werkzeug` (these are in `requirements.txt`).
- **Environment:** Requires the PostgreSQL database to be running and credentials to be defined in `.env`.

## Instructions

1. **Verify Environment:** Ensure that the Flask application and database are correctly configured. The script connects directly to the PostgreSQL database.
2. **Run Script:** Execute the crawler using Python. You can specify a limit for the number of books to process to avoid rate limits or overloading the database.
   
   ```bash
   python execution/crawl_reviews.py --limit 5
   ```

3. **Behavior:**
   - The script creates a "Bot User" (`bot@bookreviews.local`) in the database if it doesn't already exist.
   - It queries the `Books` table for books that the bot hasn't reviewed yet.
   - For each book, it attempts to fetch a snippet or description from the Google Books API. If the API fails or no data is found, it falls back to a generic, randomized template review.
   - The review and a random rating (3-5) are inserted into the `Reviews` table.

## Edge Cases

- **No Books Left:** If the script prints `No new books to review. Exiting.`, the bot has already reviewed all books in the database.
- **Connection Refused:** Ensure `db` host is reachable. The script automatically tries to use `localhost` if `DB_HOST` is set to `db` (which typically indicates a Docker environment). If your database is running on a different port or host, update the `.env` file accordingly.
- **Rate Limits:** A small randomized delay (1-2.5 seconds) is added between requests to avoid rate-limiting from the Google Books API.
