# Import Books from CSV

## Goal
Populate the database with book data from `books.csv`.

## Inputs
- `books.csv` — Source CSV file with book records (ISBN, title, author, year)
- `DATABASE_URL` — From `.env`

## Tools/Scripts
- `import.py` — Existing script that reads CSV and inserts into PostgreSQL

## Steps

1. Ensure the database is running (`docker-compose up -d`)
2. Ensure the `books` table exists (run `tables.sql` if not)
3. Run: `python import.py`

## Outputs
- Books table populated with all records from `books.csv`

## Edge Cases
- **Duplicate imports**: Running `import.py` twice may cause duplicate entries or unique constraint errors. Check if the script handles upserts.
- **Large CSV**: The CSV has ~5,000 records. Should complete in seconds with batch inserts.
- **Encoding issues**: Ensure CSV is UTF-8 encoded to avoid character errors.
