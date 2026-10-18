#!/bin/sh
echo "===== API dbt startup at $(date) ====="

cd /home/user/app/stripe_olap
dbt debug && dbt run && dbt test
echo "dbt terminé, code de sortie : $?"

# Launch FastAPI (with exec as uvicorn is the only process)
exec uvicorn src.main:app --host 0.0.0.0 --port "${CTNR_APIDBT_PORT}" --reload