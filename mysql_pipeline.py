"""Load the cleaned retail data into MySQL instead of SQLite.

Before running: py -m pip install pymysql
"""

from getpass import getpass

import pymysql

from pipeline import extract, transform


def load_to_mysql(customers, orders, quality_log, password: str, host: str, port: int, user: str) -> None:
    """Rebuild MySQL warehouse tables and load the clean records."""
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="retail_pipeline",
        charset="utf8mb4",
    )

    try:
        with connection.cursor() as cursor:
            # Drop child tables first because orders depends on customers.
            cursor.execute("DROP TABLE IF EXISTS customer_revenue_summary")
            cursor.execute("DROP TABLE IF EXISTS pipeline_quality_log")
            cursor.execute("DROP TABLE IF EXISTS fact_orders")
            cursor.execute("DROP TABLE IF EXISTS dim_customers")

            cursor.execute("""
                CREATE TABLE dim_customers (
                    customer_id VARCHAR(20) PRIMARY KEY,
                    customer_name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL,
                    city VARCHAR(100) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE fact_orders (
                    order_id VARCHAR(20) PRIMARY KEY,
                    order_date DATE NOT NULL,
                    customer_id VARCHAR(20) NOT NULL,
                    product VARCHAR(100) NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    revenue DECIMAL(12,2) NOT NULL,
                    CONSTRAINT positive_quantity CHECK (quantity > 0),
                    CONSTRAINT positive_unit_price CHECK (unit_price > 0),
                    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE pipeline_quality_log (
                    dataset VARCHAR(50) NOT NULL,
                    reason VARCHAR(100) NOT NULL,
                    rejected_rows INT NOT NULL
                )
            """)

            cursor.executemany(
                "INSERT INTO dim_customers (customer_id, customer_name, email, city) VALUES (%s, %s, %s, %s)",
                list(customers[["customer_id", "customer_name", "email", "city"]].itertuples(index=False, name=None)),
            )
            cursor.executemany(
                """INSERT INTO fact_orders
                   (order_id, order_date, customer_id, product, quantity, unit_price, revenue)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                list(orders[["order_id", "order_date", "customer_id", "product", "quantity", "unit_price", "revenue"]].itertuples(index=False, name=None)),
            )
            cursor.executemany(
                "INSERT INTO pipeline_quality_log (dataset, reason, rejected_rows) VALUES (%s, %s, %s)",
                list(quality_log.itertuples(index=False, name=None)),
            )
            cursor.execute("""
                CREATE TABLE customer_revenue_summary AS
                SELECT c.customer_id, c.customer_name, c.city,
                       COUNT(o.order_id) AS order_count,
                       ROUND(COALESCE(SUM(o.revenue), 0), 2) AS total_revenue
                FROM dim_customers AS c
                LEFT JOIN fact_orders AS o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.customer_name, c.city
            """)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main() -> None:
    print("This will load the clean pipeline data into MySQL database: retail_pipeline")
    host = input("MySQL host [localhost]: ").strip() or "localhost"
    port = int(input("MySQL port [3307]: ").strip() or "3307")
    user = input("MySQL username [root]: ").strip() or "root"
    password = getpass("Enter your MySQL root password: ")
    raw_customers, raw_orders = extract()
    customers, orders, quality_log = transform(raw_customers, raw_orders)
    load_to_mysql(customers, orders, quality_log, password, host, port, user)
    print("\nMySQL load completed successfully.")
    print(f"Loaded {len(customers)} customers and {len(orders)} valid orders.")
    print("Open MySQL Workbench and run the queries in mysql_analysis.sql.")


if __name__ == "__main__":
    main()
