SELECT
    analyst_id,
    role
FROM {{ ref('stg_raw__analysts') }}