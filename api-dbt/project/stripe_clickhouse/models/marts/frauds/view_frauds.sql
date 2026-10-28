SELECT * EXCEPT (
    reject_id
)
FROM {{ ref('stg_raw__rejects') }}