SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'activities') }}
WHERE (activity_id, __source_lsn) IN (
    SELECT activity_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'activities') }}
    GROUP BY activity_id
)