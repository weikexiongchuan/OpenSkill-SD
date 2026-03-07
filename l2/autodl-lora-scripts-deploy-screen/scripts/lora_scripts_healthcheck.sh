#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <host> <port>"
  exit 1
fi

HOST="$1"
PORT="$2"
BASE_URL="http://$HOST:$PORT"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl not found"
  exit 1
fi

if curl -fsS "$BASE_URL/api/presets" >/dev/null 2>&1; then
  echo "healthy: $BASE_URL/api/presets"
  exit 0
fi

if curl -fsS "$BASE_URL/" >/dev/null 2>&1; then
  echo "healthy: $BASE_URL/"
  exit 0
fi

echo "unhealthy: failed to reach lora-scripts API at $BASE_URL"
exit 1
