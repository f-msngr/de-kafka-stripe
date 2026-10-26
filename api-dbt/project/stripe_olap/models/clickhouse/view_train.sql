WITH customers_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'customers') }}
    WHERE (customer_id, __source_lsn) IN  (
        SELECT customer_id, max(__source_lsn)       -- prendre la dernière version de la donnée (lsn = séquence dans le WAL)
        FROM {{ source('raw', 'customers') }}
        GROUP BY customer_id
    )
),

jobs_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'jobs') }}
    WHERE (job_id, __source_lsn) IN  (
        SELECT job_id, max(__source_lsn)
        FROM {{ source('raw', 'jobs') }}
        GROUP BY job_id
    )
),

customers_w_jobs AS (
    SELECT *
    FROM customers_latest AS c
    JOIN jobs_latest AS j USING (job_id)
),

addresses_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'addresses') }}
    WHERE (address_id, __source_lsn) IN  (
        SELECT address_id, max(__source_lsn)
        FROM {{ source('raw', 'addresses') }}
        GROUP BY address_id
    )
),

customers_w_addresses AS (
    SELECT *
    FROM customers_w_jobs AS cj
    JOIN addresses_latest AS a USING (address_id)
),

cities_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'cities') }}
    WHERE (city_id, __source_lsn) IN  (
        SELECT city_id, max(__source_lsn)
        FROM {{ source('raw', 'cities') }}
        GROUP BY city_id
    )
),

customers_w_cities AS (
    SELECT *
    FROM customers_w_addresses AS ca
    JOIN cities_latest AS c USING (city_id)
),

states_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'states') }}
    WHERE (state_id, __source_lsn) IN  (
        SELECT state_id, max(__source_lsn)
        FROM {{ source('raw', 'states') }}
        GROUP BY state_id
    )
),

customers_full AS (
    SELECT *
    FROM customers_w_cities AS cc
    JOIN states_latest AS s USING (state_id)
),


transactions_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'transactions') }}
    WHERE (transaction_id, __source_lsn) IN  (
        SELECT transaction_id, max(__source_lsn)
        FROM {{ source('raw', 'transactions') }}
        GROUP BY transaction_id
    )
),

merchants_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'merchants') }}
    WHERE (merchant_id, __source_lsn) IN  (
        SELECT merchant_id, max(__source_lsn)
        FROM {{ source('raw', 'merchants') }}
        GROUP BY merchant_id
    )
),

activities_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'activities') }}
    WHERE (activity_id, __source_lsn) IN  (
        SELECT activity_id, max(__source_lsn)
        FROM {{ source('raw', 'activities') }}
        GROUP BY activity_id
    )
),

analysts_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'analysts') }}
    WHERE (analyst_id, __source_lsn) IN  (
        SELECT analyst_id, max(__source_lsn)
        FROM {{ source('raw', 'analysts') }}
        GROUP BY analyst_id
    )
),

currencies_latest AS (
    SELECT * EXCEPT (__source_lsn)
    FROM {{ source('raw', 'currencies') }}
    WHERE (currency_id, __source_lsn) IN  (
        SELECT currency_id, max(__source_lsn)
        FROM {{ source('raw', 'currencies') }}
        GROUP BY currency_id
    )
),

-- Créer une CTE pour chaque référence à currency_id dans transactions avec le nom de cette colonne (permet la jointure avec USING)
currencies_presentation AS (
    SELECT currency_id AS currency_id_presentation, currency AS currency_presentation
    FROM currencies_latest
),

currencies_received AS (
    SELECT currency_id AS currency_id_received, currency AS currency_received
    FROM currencies_latest
),

transactions_full AS (
    SELECT *
    FROM transactions_latest AS tra
    JOIN customers_full AS cus USING (customer_id)
    JOIN merchants_latest AS mer USING (merchant_id)
    JOIN activities_latest AS act USING (activity_id)
    LEFT JOIN analysts_latest AS ana USING (analyst_id)         -- utiliser LEFT JOIN car analyst_id est null pour les prédictions
    LEFT JOIN currencies_presentation AS cur_pres USING (currency_id_presentation)
    LEFT JOIN currencies_received AS cur_rec USING (currency_id_received)
)

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
FROM transactions_full

SETTINGS join_use_nulls = 1         -- pour éviter un remplacement des NULL par 0 ou par une chaîne vide