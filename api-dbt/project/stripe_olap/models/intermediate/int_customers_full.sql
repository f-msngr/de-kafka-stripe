SELECT *
FROM {{ ref('stg_raw__customers') }} AS c
JOIN {{ ref('stg_raw__jobs') }} AS j USING (job_id)
JOIN {{ ref('stg_raw__addresses') }} AS a USING (address_id)
JOIN {{ ref('stg_raw__cities') }} AS ci USING (city_id)
JOIN {{ ref('stg_raw__states') }} AS s USING (state_id)