#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: SSH_PASSWORD=<password> $0 <host> <port> <user> <pubkey-path>"
  exit 1
fi

HOST="$1"
PORT="$2"
USER_NAME="$3"
PUBKEY_PATH="$4"
PASSWORD="${SSH_PASSWORD:-}"

if [ -z "$PASSWORD" ]; then
  echo "SSH_PASSWORD is required"
  exit 1
fi

if [ ! -f "$PUBKEY_PATH" ]; then
  echo "Public key not found: $PUBKEY_PATH"
  exit 1
fi

if ! command -v expect >/dev/null 2>&1; then
  echo "expect is required but not found"
  exit 1
fi

export EXPECT_HOST="$HOST"
export EXPECT_PORT="$PORT"
export EXPECT_USER="$USER_NAME"
export EXPECT_PUBKEY="$PUBKEY_PATH"
export EXPECT_PASSWORD="$PASSWORD"

expect <<'EXP'
set timeout 120

set host $env(EXPECT_HOST)
set port $env(EXPECT_PORT)
set user $env(EXPECT_USER)
set pubkey $env(EXPECT_PUBKEY)
set password $env(EXPECT_PASSWORD)

set cmd [format {cat "%s" | ssh -p %s "%s@%s" "umask 077; mkdir -p ~/.ssh; touch ~/.ssh/authorized_keys; cat >> ~/.ssh/authorized_keys; sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys"} $pubkey $port $user $host]

spawn bash -lc $cmd
expect {
  -re "(?i)are you sure you want to continue connecting" {
    send "yes\r"
    exp_continue
  }
  -re "(?i)password:" {
    send "$password\r"
    exp_continue
  }
  eof
}

catch wait result
set exit_code [lindex $result 3]
exit $exit_code
EXP

echo "Public key installed for $USER_NAME@$HOST:$PORT"
