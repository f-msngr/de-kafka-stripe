SELECT * EXCEPT (__source_lsn)  -- retire la colonne technique du CDC
FROM {{ source('raw', 'cities') }}
WHERE (city_id, __source_lsn) IN (
    SELECT city_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'cities') }}
    GROUP BY city_id
)