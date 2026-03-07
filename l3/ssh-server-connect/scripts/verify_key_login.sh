#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <host> <port> <user> [identity-file]"
  exit 1
fi

HOST="$1"
PORT="$2"
USER_NAME="$3"
IDENTITY_FILE="${4:-$HOME/.ssh/id_ed25519}"

ssh -o BatchMode=yes -o ConnectTimeout=10 -i "$IDENTITY_FILE" -p "$PORT" "$USER_NAME@$HOST" 'echo key-login-ok'

echo "Key login verified: $USER_NAME@$HOST:$PORT"
