INSERT INTO payments.states (state)
SELECT DISTINCT state
FROM import_csv
ON CONFLICT (state) DO NOTHING;