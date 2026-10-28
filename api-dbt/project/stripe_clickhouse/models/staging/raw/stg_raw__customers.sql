SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'customers') }}
WHERE (customer_id, __source_lsn) IN (
    SELECT customer_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'customers') }}
    GROUP BY customer_id
)