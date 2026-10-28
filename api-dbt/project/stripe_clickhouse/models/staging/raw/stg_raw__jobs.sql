SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'jobs') }}
WHERE (job_id, __source_lsn) IN (
    SELECT job_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'jobs') }}
    GROUP BY job_id
)