"""A small, runnable ETL pipeline that loads to a local SQLite database."""

from pathlib import Path
import pymysql
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
DATABASE_PATH = BASE_DIR / "data" / "retail_warehouse.db"


def extract() -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(RAW_DIR / "customers_raw.csv", dtype=str)
    orders = pd.read_csv(RAW_DIR / "orders_raw.csv", dtype=str)
    return customers, orders


def transform(customers: pd.DataFrame, orders: pd.DataFrame):
    quality_log = []
    customers = customers.apply(lambda column: column.str.strip())
    customers["email"] = customers["email"].str.lower()
    duplicate_customers = customers.duplicated(subset="customer_id", keep="first")
    quality_log.append(("customers", "duplicate customer_id", int(duplicate_customers.sum())))
    customers = customers.loc[~duplicate_customers].copy()

    orders = orders.apply(lambda column: column.str.strip())
    duplicate_orders = orders.duplicated(subset="order_id", keep="first")
    quality_log.append(("orders", "duplicate order_id", int(duplicate_orders.sum())))
    orders = orders.loc[~duplicate_orders].copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce")
    orders["unit_price"] = pd.to_numeric(orders["unit_price"], errors="coerce")

    invalid_date = orders["order_date"].isna()
    invalid_quantity = orders["quantity"].isna() | (orders["quantity"] <= 0)
    invalid_price = orders["unit_price"].isna() | (orders["unit_price"] <= 0)
    known_customer = orders["customer_id"].isin(customers["customer_id"])
    quality_log.extend([
        ("orders", "invalid order_date", int(invalid_date.sum())),
        ("orders", "quantity must be positive", int(invalid_quantity.sum())),
        ("orders", "unit_price must be positive", int(invalid_price.sum())),
        ("orders", "unknown customer_id", int((~known_customer).sum())),
    ])

    orders = orders.loc[~(invalid_date | invalid_quantity | invalid_price | ~known_customer)].copy()
    orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d")
    orders["quantity"] = orders["quantity"].astype(int)
    orders["revenue"] = (orders["quantity"] * orders["unit_price"]).round(2)
    return customers, orders, pd.DataFrame(quality_log, columns=["dataset", "reason", "rejected_rows"])


def load(customers: pd.DataFrame, orders: pd.DataFrame, quality_log: pd.DataFrame) -> None:
    with pymysql.connect(DATABASE_PATH) as connection:
        connection.executescript("""
            DROP TABLE IF EXISTS customer_revenue_summary;
            DROP TABLE IF EXISTS pipeline_quality_log;
            DROP TABLE IF EXISTS fact_orders;
            DROP TABLE IF EXISTS dim_customers;
            CREATE TABLE dim_customers (customer_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, email TEXT NOT NULL, city TEXT NOT NULL);
            CREATE TABLE fact_orders (order_id TEXT PRIMARY KEY, order_date TEXT NOT NULL, customer_id TEXT NOT NULL, product TEXT NOT NULL, quantity INTEGER NOT NULL, unit_price REAL NOT NULL, revenue REAL NOT NULL, FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id));
            CREATE TABLE pipeline_quality_log (dataset TEXT NOT NULL, reason TEXT NOT NULL, rejected_rows INTEGER NOT NULL);
        """)
        customers.to_sql("dim_customers", connection, if_exists="append", index=False)
        orders.to_sql("fact_orders", connection, if_exists="append", index=False)
        quality_log.to_sql("pipeline_quality_log", connection, if_exists="append", index=False)
        connection.execute("""
            CREATE TABLE customer_revenue_summary AS
            SELECT c.customer_id, c.customer_name, c.city, COUNT(o.order_id) AS order_count,
                   ROUND(COALESCE(SUM(o.revenue), 0), 2) AS total_revenue
            FROM dim_customers AS c LEFT JOIN fact_orders AS o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_name, c.city
        """)


def main() -> None:
    raw_customers, raw_orders = extract()
    customers, orders, quality_log = transform(raw_customers, raw_orders)
    load(customers, orders, quality_log)
    print("Pipeline completed successfully")
    print(f"Raw customers: {len(raw_customers)} | loaded customers: {len(customers)}")
    print(f"Raw orders: {len(raw_orders)} | loaded valid orders: {len(orders)}")
    print("\nData-quality log:")
    print(quality_log.to_string(index=False))
    print(f"\nWarehouse created at: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
