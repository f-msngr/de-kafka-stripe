SELECT
    transaction_id,
    trans_num,
    customer_id,
    merchant_id,
    transdate_transtime,
    toDate(transdate_transtime) AS transaction_date,             -- nouvelle colonne
    toStartOfMonth(transdate_transtime) AS transaction_month,    -- nouvelle colonne
    amt,
    status,
    review_status
FROM {{ ref('stg_raw__transactions') }}