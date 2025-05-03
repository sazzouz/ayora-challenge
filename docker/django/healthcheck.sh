#!/usr/bin/env sh

set -o errexit
set -o nounset

# NOTE: Do not specify the protocol (HTTP or HTTPs) to
# not interfere with automatic redirects
/usr/bin/test "$(
  /usr/bin/curl 'localhost:8000/health/?format=json' \
  --fail \
  --write-out "%{http_code}" \
  --silent \
  --output /dev/null \
  --max-time 3
)" -eq 204
/bin/echo 'ok'
