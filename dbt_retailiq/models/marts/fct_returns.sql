{{ config(materialized='table') }}

SELECT
    transaction_id,
    invoice_no,
    stock_code,
    customer_id,
    CAST(invoice_date AS DATE) AS date_key,
    ABS(quantity) AS return_quantity,
    unit_price,
    ABS(line_total) AS return_amount,
    country
FROM {{ ref('stg_transactions') }}
WHERE is_cancellation = TRUE
