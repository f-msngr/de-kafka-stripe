SELECT
    * EXCEPT (__source_lsn, transdate_transtime, amt, amount_presentation, merch_lat, merch_long, fraud_score),  -- retire la colonne technique du CDC
    parseDateTime64BestEffort(transdate_transtime, 6, 'UTC') AS transdate_transtime,
    CAST(amt AS Decimal(20,4)) AS amt,
    CAST(amount_presentation AS Decimal(20,4)) AS amount_presentation,
    CAST(merch_lat AS Decimal(9,6)) AS merch_lat,
    CAST(merch_long AS Decimal(9,6)) AS merch_long,
    CAST(fraud_score AS Decimal(6,4)) AS fraud_score
FROM {{ source('raw', 'rejects') }}
WHERE (reject_id, __source_lsn) IN (
    SELECT reject_id, max(__source_lsn)  -- dernière version de chaque reject_id
    FROM {{ source('raw', 'rejects') }}
    GROUP BY reject_id
)