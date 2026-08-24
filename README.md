# Retail Sales Data Pipeline

A beginner-friendly ETL project: it takes messy retail CSV files, cleans and validates them with Python/Pandas, loads trusted data into a SQLite database, and creates a reporting table for SQL analysis.

## The data-engineering flow

```text
Raw CSV files  ->  Extract  ->  Transform + validate  ->  Load database  ->  SQL reporting
data/raw/          Python       Pandas + quality log     SQLite             analytics view
```

| Stage | What happens in this project | Why it matters |
| --- | --- | --- |
| Extract | Reads `customers_raw.csv` and `orders_raw.csv` | Data normally arrives from files, APIs, or another database. |
| Transform | Standardizes text, parses dates/numbers, removes duplicates, rejects bad records, calculates revenue | Raw data is rarely ready for analysis. |
| Load | Rebuilds clean tables in `data/retail_warehouse.db` | A database makes data reliable and queryable. |
| Validate | Prints row counts and rejected-record reasons | Pipelines must show what happened to the data. |
| Serve | Creates `customer_revenue_summary` | Analysts can use a ready-to-query reporting table. |

## Run it today

1. Install Python 3.11+ if it is not installed on your computer.
2. Open a terminal inside this folder.
3. Run:

```powershell
py -m pip install -r requirements.txt
py pipeline.py
```

If your machine uses `python` instead of `py`, replace `py` with `python`.

The run creates `data/retail_warehouse.db` and shows a pipeline summary. It intentionally rejects a few messy sample rows; this proves that validation is working.

## View the result with SQL

Open `data/retail_warehouse.db` in DB Browser for SQLite (optional) and run the queries in `sql/analysis.sql`.

Or use Python:

```powershell
py -c "import sqlite3; c=sqlite3.connect('data/retail_warehouse.db'); print(c.execute('SELECT * FROM customer_revenue_summary').fetchall())"
```

## PostgreSQL later

SQLite is deliberately used here so that you can finish today without installing a database server. The skills transfer directly to PostgreSQL: tables, primary keys, joins, inserts, transactions, and SQL queries. Once this runs, a next step is to replace the `sqlite3` connection in `pipeline.py` with PostgreSQL using `psycopg` and environment variables for credentials.

## MySQL version

If you already have MySQL, create the database once in MySQL Workbench:

```sql
CREATE DATABASE retail_pipeline;
```

Then install the MySQL Python driver and run the MySQL loader. It prompts for the password rather than putting it in source code.

```powershell
py -m pip install pymysql
py mysql_pipeline.py
```

Run `mysql_analysis.sql` in MySQL Workbench after the load succeeds.

## How to explain it in an interview

"I built a small ETL pipeline that ingests raw customer and order CSVs. Python and Pandas standardize fields, remove duplicates, validate dates and numeric values, and log rejected rows. The pipeline loads clean dimension and fact tables into SQLite in a transaction and generates a customer-revenue reporting table that I query with SQL."

## Git/GitHub mini workflow

```powershell
git init
git add .
git commit -m "Build retail sales ETL pipeline"
```

Create an empty GitHub repository in your browser, then follow GitHub's displayed `git remote add origin ...` and `git push` commands. Do not upload database files or real customer data; `.gitignore` already excludes the generated database.
