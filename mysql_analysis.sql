USE retail_pipeline;

-- Your final reporting table: customer revenue ranked from highest to lowest.
SELECT customer_name, city, order_count, total_revenue
FROM customer_revenue_summary
ORDER BY total_revenue DESC;

-- Revenue by product.
SELECT product, ROUND(SUM(revenue), 2) AS total_revenue, SUM(quantity) AS units_sold
FROM fact_orders
GROUP BY product
ORDER BY total_revenue DESC;

-- Evidence that the pipeline checked data quality.
SELECT dataset, reason, rejected_rows
FROM pipeline_quality_log
ORDER BY dataset, reason;
