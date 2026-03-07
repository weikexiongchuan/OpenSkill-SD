#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <host> <port> <user> <dry-run|apply> [identity-file]"
  exit 1
fi

HOST="$1"
PORT="$2"
USER_NAME="$3"
MODE="$4"
IDENTITY_FILE="${5:-$HOME/.ssh/id_ed25519}"

if [ "$MODE" != "dry-run" ] && [ "$MODE" != "apply" ]; then
  echo "Mode must be dry-run or apply"
  exit 1
fi

read -r -d '' REMOTE_SCRIPT <<'SCRIPT' || true
set -euo pipefail

CFG=/etc/ssh/sshd_config
BACKUP="${CFG}.bak.$(date +%Y%m%d-%H%M%S)"
cp "$CFG" "$BACKUP"

echo "Backup created: $BACKUP"

set_cfg() {
  local key="$1"
  local value="$2"
  if grep -Eq "^[#[:space:]]*${key}[[:space:]]+" "$CFG"; then
    sed -ri "s|^[#[:space:]]*${key}[[:space:]]+.*$|${key} ${value}|" "$CFG"
  else
    printf "%s %s\n" "$key" "$value" >> "$CFG"
  fi
}

set_cfg "PubkeyAuthentication" "yes"
set_cfg "PasswordAuthentication" "no"
set_cfg "ChallengeResponseAuthentication" "no"
set_cfg "KbdInteractiveAuthentication" "no"
set_cfg "PermitRootLogin" "prohibit-password"

if command -v sshd >/dev/null 2>&1; then
  sshd -t
fi

if command -v systemctl >/dev/null 2>&1; then
  systemctl restart ssh || systemctl restart sshd
else
  service ssh restart || service sshd restart
fi

echo "sshd hardening applied"
SCRIPT

if [ "$MODE" = "dry-run" ]; then
  echo "Dry-run remote script preview:"
  echo "$REMOTE_SCRIPT"
  exit 0
fi

ssh -i "$IDENTITY_FILE" -p "$PORT" "$USER_NAME@$HOST" "$REMOTE_SCRIPT"

echo "Hardening completed on $USER_NAME@$HOST:$PORT"
