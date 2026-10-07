#!/bin/bash
# GRANT s'applique aux tables déjà créés donc il est important que ce script s'execute après les CREATE

set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v dbname="$POSTGRES_DB" \
  -v schema_1="$DB_SRC_SCHEMA_1" \
  -v schema_2="$DB_SRC_SCHEMA_2" \
  -v dbz_user="$DEBEZIUM_USER" \
<<'EOSQL'
GRANT CONNECT ON DATABASE :"dbname" TO :"dbz_user";
GRANT USAGE ON SCHEMA :"schema_1" TO :"dbz_user";
GRANT USAGE ON SCHEMA :"schema_2" TO :"dbz_user";
GRANT SELECT ON ALL TABLES IN SCHEMA :"schema_1" TO :"dbz_user";
GRANT SELECT ON ALL TABLES IN SCHEMA :"schema_2" TO :"dbz_user";
EOSQL