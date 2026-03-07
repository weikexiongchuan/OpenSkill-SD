#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: SSH_PASSWORD=<password> $0 <local-path> <host> <port> <user> <remote-path>"
}

if [ "$#" -lt 5 ]; then
  usage
  exit 1
fi

LOCAL_PATH="$1"
HOST="$2"
PORT="$3"
USER_NAME="$4"
REMOTE_PATH="$5"
PASSWORD="${SSH_PASSWORD:-}"

if [ -z "$PASSWORD" ]; then
  echo "SSH_PASSWORD is required"
  exit 1
fi

if [ ! -e "$LOCAL_PATH" ]; then
  echo "Local path not found: $LOCAL_PATH"
  exit 1
fi

if ! command -v expect >/dev/null 2>&1; then
  echo "expect is required but not found"
  exit 1
fi

SCP_CMD="scp -P $PORT -r \"$LOCAL_PATH\" \"$USER_NAME@$HOST:$REMOTE_PATH\""

export EXPECT_SCP_CMD="$SCP_CMD"
export EXPECT_PASSWORD="$PASSWORD"

expect <<'EXP'
set timeout -1
set scp_cmd $env(EXPECT_SCP_CMD)
set password $env(EXPECT_PASSWORD)

spawn bash -lc $scp_cmd
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
