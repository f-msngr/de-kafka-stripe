#!/bin/sh
cd /home/user/app/stripe_olap
dbt debug && dbt run && dbt test
echo "dbt terminé, code de sortie : $?"
exec sleep infinity