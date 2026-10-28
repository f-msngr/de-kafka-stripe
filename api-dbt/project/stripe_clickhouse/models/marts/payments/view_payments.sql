SELECT * EXCEPT (
    job_id,
    address_id,
    city_id,
    state_id,
    customer_id,
    merchant_id,
    activity_id,
    analyst_id,
    transaction_id
)
FROM {{ ref('int_transactions_full') }}

SETTINGS join_use_nulls = 1  -- pour éviter un remplacement des NULL par 0 ou par une chaîne vide        e