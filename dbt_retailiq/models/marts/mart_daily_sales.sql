{{ config(materialized='table') }}

WITH sales AS (
    SELECT
        date_key,
        COUNT(DISTINCT invoice_no) AS order_count,
        SUM(quantity) AS units_sold,
        ROUND(SUM(gross_revenue), 2) AS gross_revenue,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM {{ ref('fct_sales') }}
    GROUP BY date_key
),
returns AS (
    SELECT
        date_key,
        ROUND(SUM(return_amount), 2) AS returns_revenue
    FROM {{ ref('fct_returns') }}
    GROUP BY date_key
)

SELECT
    s.date_key,
    s.order_count,
    s.units_sold,
    s.gross_revenue,
    COALESCE(r.returns_revenue, 0.0) AS returns_revenue,
    ROUND(s.gross_revenue - COALESCE(r.returns_revenue, 0.0), 2) AS net_revenue,
    s.active_customers
FROM sales s
LEFT JOIN returns r ON s.date_key = r.date_key
ORDER BY s.date_key
