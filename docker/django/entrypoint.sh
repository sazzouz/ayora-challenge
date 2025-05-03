#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

readonly cmd="$*"

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${REDIS_HOST:=redis}"
: "${REDIS_PORT:=6379}"

# Ensure the container starts only after the databases are ready.

wait-for-it \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --timeout=90 \
  --strict

echo "Postgres ${DB_HOST}:${DB_PORT} is up"

wait-for-it \
  --host="$REDIS_HOST" \
  --port="$REDIS_PORT" \
  --timeout=90 \
  --strict

echo "Redis ${REDIS_HOST}:${REDIS_PORT} is up"

# Evaluating passed command (do not touch):
# shellcheck disable=SC2086
exec $cmd
