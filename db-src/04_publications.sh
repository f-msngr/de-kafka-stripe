#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v schema_1="$DB_SRC_SCHEMA_1" \
  -v schema_2="$DB_SRC_SCHEMA_2" \
  -v publication="$DEBEZIUM_PUBLICATION" \
<<'EOSQL'
CREATE PUBLICATION :"publication" FOR TABLES IN SCHEMA :"schema_1", :"schema_2";
EOSQL