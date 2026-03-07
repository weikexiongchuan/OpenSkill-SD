#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <workspace-root> <server-alias>"
  exit 1
fi

WORKSPACE_ROOT="$1"
SERVER_ALIAS="$2"
SERVER_ROOT="$WORKSPACE_ROOT/servers/$SERVER_ALIAS"

mkdir -p "$WORKSPACE_ROOT/shared/datasets" \
         "$WORKSPACE_ROOT/shared/models" \
         "$WORKSPACE_ROOT/shared/logs"

mkdir -p "$SERVER_ROOT/repos" \
         "$SERVER_ROOT/data" \
         "$SERVER_ROOT/models" \
         "$SERVER_ROOT/outputs" \
         "$SERVER_ROOT/logs" \
         "$SERVER_ROOT/runs" \
         "$SERVER_ROOT/tmp" \
         "$SERVER_ROOT/cache" \
         "$SERVER_ROOT/env" \
         "$SERVER_ROOT/comfyui"

cat > "$SERVER_ROOT/server.env" <<ENV
SERVER_ALIAS=$SERVER_ALIAS
WORKSPACE_ROOT=$WORKSPACE_ROOT
SERVER_ROOT=$SERVER_ROOT
LOGIN_METHOD=unknown
SSH_ALIAS=
SSH_HOST=
SSH_PORT=
SSH_USER=
CREATED_AT=$(date -Is)
HOSTNAME=$(hostname)
ENV

ln -sfn "$SERVER_ROOT" "$WORKSPACE_ROOT/current"

echo "Workspace initialized: $SERVER_ROOT"
echo "Shortcut updated: $WORKSPACE_ROOT/current"
