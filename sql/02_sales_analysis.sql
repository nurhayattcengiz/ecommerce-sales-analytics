
USE ECommerceAnalytics;
GO

-- Monthly sales growth analysis
WITH monthly_sales AS (
    SELECT
        DATEFROMPARTS(
            YEAR(o.order_purchase_timestamp),
            MONTH(o.order_purchase_timestamp),
            1
        ) AS sales_month,
        SUM(oi.price) AS total_sales
    FROM dbo.orders AS o
    INNER JOIN dbo.order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        YEAR(o.order_purchase_timestamp),
        MONTH(o.order_purchase_timestamp)
),
sales_growth AS (
    SELECT
        sales_month,
        total_sales,
        LAG(total_sales) OVER (
            ORDER BY sales_month
        ) AS previous_month_sales
    FROM monthly_sales
)
SELECT
    sales_month,
    total_sales,
    previous_month_sales,
    ROUND(
        (total_sales - previous_month_sales)
        * 100.0 / NULLIF(previous_month_sales, 0),
        2
    ) AS growth_percentage
FROM sales_growth
ORDER BY sales_month;



-- Rank months by total product sales
WITH monthly_sales AS (
    SELECT
        YEAR(o.order_purchase_timestamp) AS sales_year,
        MONTH(o.order_purchase_timestamp) AS sales_month,
        SUM(oi.price) AS total_sales
    FROM dbo.orders AS o
    INNER JOIN dbo.order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        YEAR(o.order_purchase_timestamp),
        MONTH(o.order_purchase_timestamp)
)
SELECT
    sales_year,
    sales_month,
    total_sales,
    RANK() OVER (
-- Rank months by total product sales
WITH monthly_sales AS (
    SELECT
        YEAR(o.order_purchase_timestamp) AS sales_year,
        MONTH(o.order_purchase_timestamp) AS sales_month,
        SUM(oi.price) AS total_sales
    FROM dbo.orders AS o
    INNER JOIN dbo.order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        YEAR(o.order_purchase_timestamp),
        MONTH(o.order_purchase_timestamp)
)
SELECT
    sales_year,
    sales_month,
    total_sales,
    RANK() OVER (
        ORDER BY total_sales DESC
    ) AS sales_rank
FROM monthly_sales
ORDER BY sales_rank;

        ORDER BY total_sales DESC
    ) AS sales_rank
FROM monthly_sales
ORDER BY sales_rank;
