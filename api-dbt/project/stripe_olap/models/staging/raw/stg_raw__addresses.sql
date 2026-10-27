SELECT
    * EXCEPT (__source_lsn, lat, long),  -- retire la colonne technique du CDC
    CAST(lat AS Decimal(9,6)) AS lat,
    CAST(long AS Decimal(9,6)) AS long
FROM {{ source('raw', 'addresses') }}
WHERE (address_id, __source_lsn) IN (
    SELECT address_id, max(__source_lsn)  -- dernière version de chaque clé (lsn = séquence dans le WAL)
    FROM {{ source('raw', 'addresses') }}
    GROUP BY address_id
)