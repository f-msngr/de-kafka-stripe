SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'analysts') }}
WHERE (analyst_id, __source_lsn) IN (
    SELECT analyst_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'analysts') }}
    GROUP BY analyst_id
)