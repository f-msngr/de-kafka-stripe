#!/bin/bash

# 1. Journaux d'api-dbt (suivi continu)
gnome-terminal -- bash -c 'docker compose logs -f --tail 50 api-dbt'
 
# 2. Journaux d'api-gateway (suivi continu)
gnome-terminal -- bash -c 'docker compose logs -f --tail 50 api-gateway'
 
# 3. Statut du run dbt vu par api-gateway, puis shell dans le conteneur api-gateway
gnome-terminal -- bash -c 'docker compose exec api-gateway sh -c '\''curl -sf "http://127.0.0.1:${CTNR_APIGATEWAY_PORT}/run-status"; echo; exec bash'\'''
 
# 4. Fichier d'état écrit par api-dbt, puis shell dans le conteneur api-dbt
gnome-terminal -- bash -c 'docker compose exec api-dbt sh -c '\''cat "$DBT_RUN_STATUS_FILE"; echo; exec bash'\'''