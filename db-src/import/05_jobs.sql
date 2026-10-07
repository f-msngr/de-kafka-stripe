INSERT INTO payments.jobs (job)
SELECT DISTINCT job
FROM import_csv
ON CONFLICT (job) DO NOTHING;