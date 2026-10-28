SELECT
    transaction_id,
    trans_num,
    CAST(analyst_id AS Int32) AS analyst_id,        -- analyst_id ne peut pas être nul car on filtre les reviewed
    transdate_transtime,
    toDate(transdate_transtime) AS transaction_date,        -- nouvelle colonne : dimension intégrée dans le fait
    toStartOfMonth(transdate_transtime) AS transaction_month,   -- nouvelle colonne : dimension intégrée dans le fait
    CAST(verdict_at AS DateTime64(6, 'UTC')) AS verdict_at,     -- verdict_at ne peut pas être nul car on filtre les reviewed
    toDate(verdict_at) AS verdict_date,                         -- verdict_at ne peut pas être nul car on filtre les reviewed
    toStartOfMonth(verdict_at) AS verdict_month,                -- verdict_at ne peut pas être nul car on filtre les reviewed
    dateDiff('second', transdate_transtime, verdict_at) AS review_delay_s,
    CAST(is_fraud AS Bool) AS is_fraud,                         -- is_fraud ne peut pas être nul car on filtre les reviewed
    amt
FROM {{ ref('stg_raw__transactions') }}
WHERE review_status = 'reviewed'
  AND verdict_at IS NOT NULL