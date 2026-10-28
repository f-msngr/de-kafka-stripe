SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'currencies') }}
WHERE (currency_id, __source_lsn) IN (
    SELECT currency_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'currencies') }}
    GROUP BY currency_id
)