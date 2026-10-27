{{ config(materialized='table') }}

SELECT
    customer_id,
    MAX(country) AS country,
    MIN(invoice_date) AS first_purchase_date,
    MAX(invoice_date) AS last_purchase_date,
    COUNT(DISTINCT invoice_no) AS total_orders,
    ROUND(SUM(CASE WHEN is_cancellation = FALSE THEN line_total ELSE 0 END), 2) AS total_spend,
    CASE WHEN COUNT(DISTINCT invoice_no) > 1 THEN TRUE ELSE FALSE END AS is_repeat_customer
FROM {{ ref('stg_transactions') }}
WHERE customer_id != 'guest_checkout'
GROUP BY customer_id
