#!/usr/bin/env bash
set -euo pipefail

KEY_PATH="${1:-$HOME/.ssh/id_ed25519}"
COMMENT="${2:-autodl-key}"

mkdir -p "$(dirname "$KEY_PATH")"
chmod 700 "$(dirname "$KEY_PATH")"

if [ -f "$KEY_PATH" ] && [ -f "$KEY_PATH.pub" ]; then
  echo "Key already exists: $KEY_PATH"
else
  ssh-keygen -t ed25519 -a 64 -N "" -f "$KEY_PATH" -C "$COMMENT"
  echo "Created key: $KEY_PATH"
fi

echo "Public key:"
cat "$KEY_PATH.pub"
