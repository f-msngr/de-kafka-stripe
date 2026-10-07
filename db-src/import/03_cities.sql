INSERT INTO payments.cities (city, zip, city_pop, state_id)
SELECT DISTINCT ON (s.city, st.state_id, s.zip)
       s.city, s.zip, s.city_pop::int, st.state_id
FROM import_csv s
JOIN payments.states st ON st.state = s.state
ORDER BY s.city, st.state_id, s.zip, s.trans_date_trans_time
ON CONFLICT (city, state_id, zip) DO NOTHING;