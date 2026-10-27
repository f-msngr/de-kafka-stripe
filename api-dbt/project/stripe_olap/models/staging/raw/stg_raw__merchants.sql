SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'merchants') }}
WHERE (merchant_id, __source_lsn) IN (
    SELECT merchant_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'merchants') }}
    GROUP BY merchant_id
)