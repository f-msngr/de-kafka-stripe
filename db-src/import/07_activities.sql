INSERT INTO payments.activities (category)
SELECT DISTINCT category
FROM import_csv
ON CONFLICT (category) DO NOTHING;