WITH
-- Une CTE par référence à currency_id dans transactions, avec le nom de colonne de transactions (permet la jointure avec USING)
currencies_presentation AS (
    SELECT currency_id AS currency_id_presentation, currency AS currency_presentation
    FROM {{ ref('stg_raw__currencies') }}
),

currencies_received AS (
    SELECT currency_id AS currency_id_received, currency AS currency_received
    FROM {{ ref('stg_raw__currencies') }}
)

SELECT *
FROM {{ ref('stg_raw__transactions') }} AS tra
JOIN {{ ref('int_customers_full') }} AS cus USING (customer_id)
JOIN {{ ref('stg_raw__merchants') }} AS mer USING (merchant_id)
JOIN {{ ref('stg_raw__activities') }} AS act USING (activity_id)
LEFT JOIN {{ ref('stg_raw__analysts') }} AS ana USING (analyst_id)  -- LEFT JOIN car analyst_id est null pour les prédictions
LEFT JOIN currencies_presentation AS cur_pres USING (currency_id_presentation)
LEFT JOIN currencies_received AS cur_rec USING (currency_id_received)

SETTINGS join_use_nulls = 1  -- évite le remplacement des NULL par 0 ou par une chaîne vide