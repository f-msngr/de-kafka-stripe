SELECT
    * EXCEPT (__source_lsn, transdate_transtime, amt, amount_presentation, currency_rate, refunded_at, fraud_score, verdict_at, merch_lat, merch_long),  -- retire la colonne technique du CDC + les colonnes en String
    parseDateTime64BestEffort(transdate_transtime, 6, 'UTC') AS transdate_transtime,
    CAST(amt AS Decimal(20,4)) AS amt,
    CAST(amount_presentation AS Decimal(20,4)) AS amount_presentation,
    CAST(currency_rate AS Decimal(20,10)) AS currency_rate,
    parseDateTime64BestEffortOrNull(refunded_at, 6, 'UTC') AS refunded_at,
    CAST(fraud_score AS Nullable(Decimal(6,4))) AS fraud_score,
    parseDateTime64BestEffortOrNull(verdict_at, 6, 'UTC') AS verdict_at,
    CAST(merch_lat AS Decimal(9,6)) AS merch_lat,
    CAST(merch_long AS Decimal(9,6)) AS merch_long
FROM {{ source('raw', 'transactions') }}
WHERE (transaction_id, __source_lsn) IN (
    SELECT transaction_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'transactions') }}
    GROUP BY transaction_id
)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       