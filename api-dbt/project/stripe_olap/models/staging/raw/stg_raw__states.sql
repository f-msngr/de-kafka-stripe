SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'states') }}
WHERE (state_id, __source_lsn) IN (
    SELECT state_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'states') }}
    GROUP BY state_id
)