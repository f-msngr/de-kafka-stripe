INSERT INTO payments.customers (first_name, last_name, gender, dob, job_id, address_id)
SELECT DISTINCT ON (s."first", s."last", s.dob)
       s."first", s."last", s.gender, s.dob::date, j.job_id, a.address_id
FROM import_csv s
JOIN payments.jobs j      ON j.job = s.job
JOIN payments.states st   ON st.state = s.state
JOIN payments.cities c    ON c.city = s.city AND c.state_id = st.state_id AND c.zip = s.zip
JOIN payments.addresses a ON a.street = s.street
                         AND a.lat = s.lat::numeric(9,6)
                         AND a.long = s."long"::numeric(9,6)
                         AND a.city_id = c.city_id
ORDER BY s."first", s."last", s.dob, s.trans_date_trans_time
ON CONFLICT (first_name, last_name, dob) DO NOTHING;