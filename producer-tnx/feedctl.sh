#!/bin/sh
# Usage : ./producer-tnx/feedctl.sh start|halt
SERVICE="producer-tnx"                  # nom du service dans docker-compose.yaml
STATE_FILE="/tmp/producer_state"        # même chemin que STATE_FILE dans worker_incoming_tnx.py

case "$1" in
  start|halt) ;;
  *) echo "usage : $0 start|halt" >&2; exit 1 ;;
esac

cd "$(dirname "$0")/.." || exit 1       # dossier du docker-compose.yaml (le script est dans producer-tnx/)
docker compose exec -T "$SERVICE" sh -c "echo $1 > $STATE_FILE" && echo "état : $1"