SELECT * EXCEPT (
    job_id,
    address_id,
    city_id,
    state_id,
    customer_id,
    merchant_id,
    activity_id,
    analyst_id,
    transaction_id,
    ip_geoloc,
    device_type,
    amount_presentation,
    currency_id_presentation,
    currency_presentation,
    currency_received,
    currency_rate,
    status,
    fraud_score,
    model_version,
    review_status,
    verdict_at,
    role,
    is_fraud,
    refunded_at
)
FROM {{ ref('int_transactions_full') }}

SETTINGS join_use_nulls = 1  -- pour éviter un remplacement des NULL par 0 ou par une chaîne vide