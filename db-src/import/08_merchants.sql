INSERT INTO payments.merchants (merchant)
SELECT DISTINCT merchant
FROM import_csv
ON CONFLICT (merchant) DO NOTHING;