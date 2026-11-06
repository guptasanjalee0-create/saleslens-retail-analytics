-- Run these queries after `python run_analysis.py` has created data/saleslens.sqlite.

-- 1. Overall KPIs
SELECT ROUND(SUM(revenue), 2) AS total_revenue_gbp,
       SUM(quantity) AS units_sold,
       COUNT(DISTINCT invoice_no) AS invoices,
       COUNT(DISTINCT stock_code) AS products,
       COUNT(DISTINCT customer_id) AS customers
FROM retail_transactions;

-- 2. Monthly revenue
SELECT invoice_month, ROUND(SUM(revenue), 2) AS revenue_gbp
FROM retail_transactions
GROUP BY invoice_month ORDER BY invoice_month;

-- 3. Top 10 products by revenue
SELECT stock_code, description, SUM(quantity) AS units_sold,
       ROUND(SUM(revenue), 2) AS revenue_gbp
FROM retail_transactions
GROUP BY stock_code, description
ORDER BY revenue_gbp DESC LIMIT 10;

-- 4. Top 10 countries by revenue
SELECT country, ROUND(SUM(revenue), 2) AS revenue_gbp
FROM retail_transactions
GROUP BY country ORDER BY revenue_gbp DESC LIMIT 10;

-- 5. Average order value
SELECT ROUND(AVG(order_total), 2) AS average_order_value_gbp
FROM (SELECT invoice_no, SUM(revenue) AS order_total
      FROM retail_transactions GROUP BY invoice_no);

-- 6. Order count by hour
SELECT invoice_hour, COUNT(DISTINCT invoice_no) AS order_count
FROM retail_transactions GROUP BY invoice_hour ORDER BY invoice_hour;

-- 7. Repeat customers (more than one distinct invoice)
SELECT customer_id, COUNT(DISTINCT invoice_no) AS order_count,
       ROUND(SUM(revenue), 2) AS customer_revenue_gbp
FROM retail_transactions WHERE customer_id IS NOT NULL
GROUP BY customer_id HAVING COUNT(DISTINCT invoice_no) > 1
ORDER BY order_count DESC;

-- 8. Revenue concentration by product category is not available in the source data;
-- use product descriptions/stock codes carefully and do not invent categories.

-- 9. Rank products by revenue using a window function
WITH product_revenue AS (
    SELECT stock_code, description, SUM(revenue) AS revenue_gbp
    FROM retail_transactions
    GROUP BY stock_code, description
)
SELECT stock_code, description, ROUND(revenue_gbp, 2) AS revenue_gbp,
       RANK() OVER (ORDER BY revenue_gbp DESC) AS revenue_rank
FROM product_revenue
ORDER BY revenue_rank
LIMIT 10;

-- 10. Customer purchase frequency using a CTE
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS invoice_count,
           ROUND(SUM(revenue), 2) AS lifetime_revenue_gbp
    FROM retail_transactions
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT * FROM customer_orders
WHERE invoice_count >= 2
ORDER BY lifetime_revenue_gbp DESC;

-- 11. Monthly revenue with previous-month comparison (LAG window function)
WITH monthly AS (
    SELECT invoice_month, SUM(revenue) AS revenue_gbp
    FROM retail_transactions GROUP BY invoice_month
)
SELECT invoice_month, ROUND(revenue_gbp, 2) AS revenue_gbp,
       ROUND(LAG(revenue_gbp) OVER (ORDER BY invoice_month), 2) AS previous_month_revenue_gbp
FROM monthly
ORDER BY invoice_month;
