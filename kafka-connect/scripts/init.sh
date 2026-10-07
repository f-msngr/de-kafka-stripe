#!/bin/sh
set -e
for f in /configs/*.json; do
  name="${PROJECT_NAME}-$(basename "$f" .json)"
  curl  --fail-with-body  -sS -X PUT -H "Content-Type: application/json" --data @"$f" \
    "http://${SRVC_CONNECT}:${CTNR_CONNECT_PORT}/connectors/${name}/config"
  echo "🟢 Kafka ${name} uploaded"
  sleep 5   # laisse le temps aux tasks de démarrer
  curl -fsS "http://${SRVC_CONNECT}:${CTNR_CONNECT_PORT}/connectors/${name}/status"
  echo
done