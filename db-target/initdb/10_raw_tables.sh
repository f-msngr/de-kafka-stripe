#!/bin/bash
set -e   # arrête le script à la première erreur, pour que l'échec soit visible dans les logs
# --multiquery permet d’exécuter plusieurs CREATE TABLE d’un même fichier.
clickhouse-client --host 127.0.0.1 --multiquery --user "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" --database "$CLICKHOUSE_DB" < /sql/10_raw_tables_from_dbsrc.sql