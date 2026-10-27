{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ ref('silver_transactions') }}
)

SELECT
    transaction_id,
    batch_id,
    invoice_no,
    stock_code,
    description,
    quantity,
    invoice_date,
    CAST(invoice_date AS DATE) AS date_key,
    unit_price,
    customer_id,
    country,
    is_cancellation,
    is_guest_checkout,
    line_total
FROM source
