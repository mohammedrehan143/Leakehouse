{{ config(materialized='table') }}

SELECT
    transaction_id,
    invoice_no,
    stock_code,
    customer_id,
    CAST(invoice_date AS DATE) AS date_key,
    quantity,
    unit_price,
    line_total AS gross_revenue,
    country
FROM {{ ref('stg_transactions') }}
WHERE is_cancellation = FALSE
  AND quantity > 0
  AND unit_price > 0
