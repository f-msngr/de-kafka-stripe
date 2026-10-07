#!/bin/sh
set -e
curl -fs http://localhost:${REST_PORT}/connectors > /dev/null