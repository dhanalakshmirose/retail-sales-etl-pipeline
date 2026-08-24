# Retail Sales ETL Pipeline

A beginner-friendly Data Engineering project that extracts retail data from CSV files, cleans and validates it with Python and Pandas, loads trusted data into MySQL, and creates SQL revenue reports.

## Pipeline flow

```text
Raw CSV files → Python/Pandas cleaning → MySQL database → SQL reporting
```

## Tools used

- Python
- Pandas
- MySQL
- SQL
- PyMySQL
- Git/GitHub

## What the pipeline does

1. Reads raw customer and order CSV files.
2. Removes extra spaces and standardizes email addresses.
3. Detects and removes duplicate customer and order records.
4. Validates order dates, quantities, prices, and customer IDs.
5. Calculates revenue for valid orders.
6. Loads clean customers and orders into MySQL.
7. Creates a customer-revenue summary table.
8. Stores rejected-record reasons in a data-quality log.

## Project structure

```text
data/raw/
  customers_raw.csv
  orders_raw.csv

pipeline.py
mysql_pipeline.py
mysql_analysis.sql
requirements.txt
```

## How to run

Create the MySQL database first:

```sql
CREATE DATABASE retail_pipeline;
```

Install Python packages:

```powershell
py -m pip install -r requirements.txt
```

Run the pipeline:

```powershell
py mysql_pipeline.py
```

The script asks for your MySQL host, port, username, and password.

For this project:

```text
Host: localhost
Port: 3307
Username: root
```

## Example data-quality checks

The pipeline rejects:

- Duplicate customer IDs
- Duplicate order IDs
- Invalid order dates
- Zero or negative quantities
- Zero or negative prices
- Orders with unknown customer IDs

## Example SQL report

```sql
USE retail_pipeline;

SELECT customer_name, city, order_count, total_revenue
FROM customer_revenue_summary
ORDER BY total_revenue DESC;
```

## Result

The pipeline successfully loaded 4 clean customers and 3 valid orders into MySQL after validating the raw data.

## What I learned

- ETL pipeline basics: Extract, Transform, Load
- Data cleaning and validation with Pandas
- Loading Python data into MySQL
- SQL reporting and aggregation
- Using GitHub to document a project
- 
