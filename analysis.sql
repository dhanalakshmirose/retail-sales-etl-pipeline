-- 1. Top customers by total revenue
SELECT customer_name, city, order_count, total_revenue
FROM customer_revenue_summary
ORDER BY total_revenue DESC;

-- 2. Revenue by product
SELECT product, ROUND(SUM(revenue), 2) AS total_revenue, SUM(quantity) AS units_sold
FROM fact_orders
GROUP BY product
ORDER BY total_revenue DESC;

-- 3. Data-quality results from the latest run
SELECT dataset, reason, rejected_rows
FROM pipeline_quality_log
ORDER BY dataset, reason;
