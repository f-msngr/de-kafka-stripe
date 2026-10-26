WITH rejects_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'rejects') }}
    WHERE (reject_id, __source_lsn) IN  (
        SELECT reject_id, max(__source_lsn)
        FROM {{ source('raw', 'rejects') }}
        GROUP BY reject_id
    )
),

SELECT * EXCEPT (
    reject_id
)
FROM rejects_latest