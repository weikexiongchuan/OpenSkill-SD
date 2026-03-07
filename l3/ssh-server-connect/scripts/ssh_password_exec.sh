#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: SSH_PASSWORD=<password> $0 <host> <port> <user> -- <remote command...>"
}

if [ "$#" -lt 5 ]; then
  usage
  exit 1
fi

HOST="$1"
PORT="$2"
USER_NAME="$3"
shift 3

if [ "$1" != "--" ]; then
  usage
  exit 1
fi
shift

if [ "$#" -lt 1 ]; then
  echo "Remote command is required"
  exit 1
fi

PASSWORD="${SSH_PASSWORD:-}"
if [ -z "$PASSWORD" ]; then
  echo "SSH_PASSWORD is required"
  exit 1
fi

if ! command -v expect >/dev/null 2>&1; then
  echo "expect is required but not found"
  exit 1
fi

printf -v REMOTE_RAW "%q " "$@"
REMOTE_RAW="${REMOTE_RAW% }"
export EXPECT_HOST="$HOST"
export EXPECT_PORT="$PORT"
export EXPECT_USER="$USER_NAME"
export EXPECT_REMOTE_CMD="$REMOTE_RAW"
export EXPECT_PASSWORD="$PASSWORD"

expect <<'EXP'
set timeout -1
set host $env(EXPECT_HOST)
set port $env(EXPECT_PORT)
set user $env(EXPECT_USER)
set remote_cmd $env(EXPECT_REMOTE_CMD)
set password $env(EXPECT_PASSWORD)

spawn ssh -o StrictHostKeyChecking=accept-new -p $port "$user@$host" $remote_cmd
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
