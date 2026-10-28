/*
union des transactions et des rejets
une colonne origin pour conserver l'origine de la fraude : 
    rejets = évitée ; init ou reviewed frauduleux = subie
*/

SELECT
    trans_num,
    'rejected' AS origin,
    merchant_id,
    transdate_transtime,
    toDate(transdate_transtime) AS fraud_date,           -- nouvelle colonne : dimension intégrée dans le fait
    toStartOfMonth(transdate_transtime) AS fraud_month,  -- nouvelle colonne : dimension intégrée dans le fait
    amt,
    merch_lat,
    merch_long,
    CAST(fraud_score AS Nullable(Decimal(6,4))) AS fraud_score
FROM {{ ref('stg_raw__rejects') }}

UNION ALL

SELECT
    trans_num,
    if(review_status = 'init', 'init', 'reviewed') AS origin,
    merchant_id,
    transdate_transtime,
    toDate(transdate_transtime) AS fraud_date,          -- nouvelle colonne : dimension intégrée dans le fait
    toStartOfMonth(transdate_transtime) AS fraud_month, -- nouvelle colonne : dimension intégrée dans le fait
    amt,
    merch_lat,
    merch_long,
    CAST(fraud_score AS Nullable(Decimal(6,4))) AS fraud_score
FROM {{ ref('stg_raw__transactions') }}
WHERE review_status IN ('init', 'reviewed')
  AND is_fraud