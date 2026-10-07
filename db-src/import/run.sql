-- Import initial : fichier maître, à lancer depuis le dossier ../init/
-- Garantit le lancement des imports dans une seule transaction
\set ON_ERROR_STOP on
 
BEGIN;
SET LOCAL TIME ZONE 'UTC';
 
\ir 01_staging.sql
\ir 02_states.sql
\ir 03_cities.sql
\ir 04_addresses.sql
\ir 05_jobs.sql
\ir 06_customers.sql
\ir 07_activities.sql
\ir 08_merchants.sql
\ir 09_default_values.sql
\ir 10_transactions.sql
\ir 11_checks.sql
 
COMMIT;