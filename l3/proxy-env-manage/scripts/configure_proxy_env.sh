#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <workspace-root> <proxy-url|none>"
  exit 1
fi

WORKSPACE_ROOT="$1"
PROXY_URL="$2"
PROXY_FILE="$WORKSPACE_ROOT/.proxy_env"

mkdir -p "$WORKSPACE_ROOT"

if [ "${PROXY_URL,,}" = "none" ]; then
  rm -f "$PROXY_FILE"
  echo "Proxy file removed: $PROXY_FILE"
  exit 0
fi

cat > "$PROXY_FILE" <<ENV
export http_proxy="$PROXY_URL"
export https_proxy="$PROXY_URL"
export all_proxy="$PROXY_URL"
export HTTP_PROXY="$PROXY_URL"
export HTTPS_PROXY="$PROXY_URL"
export ALL_PROXY="$PROXY_URL"
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"
ENV

echo "Proxy env written: $PROXY_FILE"
echo "Load with: source $PROXY_FILE"
