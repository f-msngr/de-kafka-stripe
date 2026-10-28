SELECT
    merchant_id,
    merchant
FROM {{ ref('stg_raw__merchants') }}