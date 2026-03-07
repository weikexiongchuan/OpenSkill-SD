#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: SSH_PASSWORD=<password> $0 <host> <ssh-port> <user> <local-port> <remote-host> <remote-port> [log-file] [pid-file]"
}

if [ "$#" -lt 6 ]; then
  usage
  exit 1
fi

HOST="$1"
SSH_PORT="$2"
USER_NAME="$3"
LOCAL_PORT="$4"
REMOTE_HOST="$5"
REMOTE_PORT="$6"
LOG_FILE="${7:-$HOME/.ssh/ssh-tunnel-${USER_NAME}@${HOST}-${LOCAL_PORT}.log}"
PID_FILE="${8:-$HOME/.ssh/ssh-tunnel-${USER_NAME}@${HOST}-${LOCAL_PORT}.pid}"
PASSWORD="${SSH_PASSWORD:-}"

if [ -z "$PASSWORD" ]; then
  echo "SSH_PASSWORD is required"
  exit 1
fi

if ! command -v expect >/dev/null 2>&1; then
  echo "expect is required but not found"
  exit 1
fi

if ! command -v lsof >/dev/null 2>&1; then
  echo "lsof is required but not found"
  exit 1
fi

mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$PID_FILE")"

if lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Local port already listening: $LOCAL_PORT"
  lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN
  exit 0
fi

export EXPECT_HOST="$HOST"
export EXPECT_PORT="$SSH_PORT"
export EXPECT_USER="$USER_NAME"
export EXPECT_LOCAL_PORT="$LOCAL_PORT"
export EXPECT_REMOTE_HOST="$REMOTE_HOST"
export EXPECT_REMOTE_PORT="$REMOTE_PORT"
export EXPECT_PASSWORD="$PASSWORD"

expect <<'EXP' >"$LOG_FILE" 2>&1
set timeout 120

set host $env(EXPECT_HOST)
set port $env(EXPECT_PORT)
set user $env(EXPECT_USER)
set local_port $env(EXPECT_LOCAL_PORT)
set remote_host $env(EXPECT_REMOTE_HOST)
set remote_port $env(EXPECT_REMOTE_PORT)
set password $env(EXPECT_PASSWORD)

spawn ssh -fN \
  -L "${local_port}:${remote_host}:${remote_port}" \
  -p $port \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -o StrictHostKeyChecking=accept-new \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  "$user@$host"

expect {
  -re {(?i)are you sure you want to continue connecting} {
    send "yes\r"
    exp_continue
  }
  -re {(?i)password:} {
    send "$password\r"
    exp_continue
  }
  eof
}

catch wait result
set exit_code [lindex $result 3]
exit $exit_code
EXP

for _ in $(seq 1 20); do
  if lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    TUNNEL_PID="$(lsof -tiTCP:"$LOCAL_PORT" -sTCP:LISTEN | head -n 1)"
    printf '%s\n' "$TUNNEL_PID" > "$PID_FILE"
    echo "Tunnel ready: 127.0.0.1:$LOCAL_PORT -> $REMOTE_HOST:$REMOTE_PORT"
    echo "PID: $TUNNEL_PID"
    echo "Log file: $LOG_FILE"
    echo "PID file: $PID_FILE"
    exit 0
  fi
  sleep 0.5
done

echo "Tunnel did not start on local port $LOCAL_PORT" >&2
sed -n '1,120p' "$LOG_FILE" >&2 || true
exit 1
