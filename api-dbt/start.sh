#!/bin/sh
echo "===== API dbt startup at $(date) ====="

DBT_PATH=/home/user/app

echo "==> dbt startup from $DBT_PATH"
cd $DBT_PATH
# dbt debug && dbt run && dbt test
dbt debug
echo "dbt terminé, code de sortie : $?"

# Launch FastAPI (with exec as uvicorn is the only process)
UVICORN_PATH=/home/user/app/src
cd $UVICORN_PATH

echo "==> uvicorn startup from $UVICORN_PATH"
exec uvicorn src.main:app --host 0.0.0.0 --port "${CTNR_APIDBT_PORT}" --reload