INSERT INTO payments.addresses (street, lat, long, city_id)
SELECT DISTINCT s.street, s.lat::numeric(9,6), s."long"::numeric(9,6), c.city_id
FROM import_csv s
JOIN payments.states st ON st.state = s.state
JOIN payments.cities c  ON c.city = s.city AND c.state_id = st.state_id AND c.zip = s.zip
ON CONFLICT (street, lat, long, city_id) DO NOTHING;