{{ config(materialized='table') }}

SELECT
    stock_code,
    MAX(description) AS description,
    ROUND(AVG(unit_price), 2) AS typical_unit_price,
    SUM(CASE WHEN is_cancellation = FALSE THEN quantity ELSE 0 END) AS total_units_sold,
    ROUND(SUM(CASE WHEN is_cancellation = FALSE THEN line_total ELSE 0 END), 2) AS total_revenue
FROM {{ ref('stg_transactions') }}
GROUP BY stock_code
