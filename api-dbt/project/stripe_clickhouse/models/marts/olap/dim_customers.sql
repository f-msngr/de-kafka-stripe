SELECT
    customer_id,
    first_name,
    last_name,
    gender,
    dob,
    job,
    street,
    lat,
    long,
    city,
    zip,
    city_pop,
    state
FROM {{ ref('int_customers_full') }}