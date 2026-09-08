# Application App

Two Streamlit apps backed by SQL Server:

| App                       | File                         | What it does                                                                                                                                                  |
| ------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Accommodation Application | `app/accommodation_app.py` | Public-facing form — applicants submit their details, which are written straight to SQL Server. Includes an admin expander to view/download all submissions. |
| Data Explorer             | `app/data_explorer_app.py` | Upload a CSV and push it into SQL Server, or browse existing tables and run ad-hoc SQL queries.                                                               |

Both apps share one connection config (`app/config.py`), loaded from a single `.env` file — no server names, drivers, or database/table names are hardcoded.

## Requirements

- Python 3.9+
- SQL Server reachable from your machine, with Windows Authentication (Trusted Connection)
- An ODBC Driver for SQL Server installed (17 or 18)

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your connection
cp .env.example .env
# then edit .env with your server/database details

# 3. Create the database + table
sqlcmd -S YOUR_SERVER\INSTANCE -E -i sql/001_create_database.sql
sqlcmd -S YOUR_SERVER\INSTANCE -E -i sql/002_create_tables.sql

# 4. (optional) Load sample data
python app/seed.py

# 5. Run an app
streamlit run app/accommodation_app.py
streamlit run app/data_explorer_app.py
```

## Configuration (`.env`)

Copy `.env.example` to `.env` and fill in your own values. `.env` is gitignored and never committed.

| Variable                   | Example                           | Used by                                                                 |
| -------------------------- | --------------------------------- | ----------------------------------------------------------------------- |
| `SQL_SERVER`             | `GHOST\MSSQLSERVER02`           | both apps                                                               |
| `SQL_DRIVER`             | `ODBC Driver 17 for SQL Server` | both apps (default driver; Data Explorer lets you override per session) |
| `ACCOMMODATION_DATABASE` | `stg_booking_com`               | Accommodation Application                                               |
| `ACCOMMODATION_TABLE`    | `dbo.stg_booking_com_raw`       | Accommodation Application                                               |

## Database setup

Run once, in order, against your SQL Server instance (SSMS or `sqlcmd`):

1. `sql/001_create_database.sql` — creates the `stg_booking_com` database
2. `sql/002_create_tables.sql` — creates `dbo.stg_booking_com_raw`
3. `sql/003_seed_data.sql` — optional: inserts 4 sample rows (skips if the table already has data)

Prefer Python? `python app/seed.py` does the same thing as step 3, using your `.env` connection settings instead of a direct `sqlcmd` connection.

## Running the apps

```bash
streamlit run app/accommodation_app.py    # http://localhost:8501
streamlit run app/data_explorer_app.py    # run on a different port if both are open at once:
streamlit run app/data_explorer_app.py --server.port 8502
```

## Project structure

```
.
├── app/
│   ├── config.py                # loads .env, builds SQL Server connections
│   ├── accommodation_app.py     # accommodation form
│   ├── data_explorer_app.py     # CSV upload + table browser
│   └── seed.py                  # sample-data seeder
├── sql/
│   ├── 001_create_database.sql
│   ├── 002_create_tables.sql
│   └── 003_seed_data.sql
├── data/exports/                 # CSV downloads land here (gitignored)
├── .env                          # your local config — gitignored, never committed
├── .env.example                  # template, committed
└── requirements.txt
```

## Data privacy

`data/exports/` holds CSV downloads from the admin view — real applicant names, ID numbers, emails and phone numbers. This folder is gitignored: never commit files from it, and never paste its contents elsewhere.
