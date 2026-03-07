#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  $0 start <session-name> <log-file> -- <command...>
  $0 status <session-name>
  $0 attach <session-name>
  $0 stop <session-name>
  $0 list
USAGE
}

if [ "$#" -lt 1 ]; then
  usage
  exit 1
fi

ACTION="$1"
shift

has_session() {
  local name="$1"
  screen -ls 2>/dev/null | grep -q "[.]${name}[[:space:]]"
}

case "$ACTION" in
  start)
    if [ "$#" -lt 4 ]; then
      usage
      exit 1
    fi
    SESSION_NAME="$1"
    LOG_FILE="$2"
    shift 2

    if [ "$1" != "--" ]; then
      echo "Missing -- before command"
      exit 1
    fi
    shift

    if [ "$#" -lt 1 ]; then
      echo "No command provided"
      exit 1
    fi

    if has_session "$SESSION_NAME"; then
      echo "Session already exists: $SESSION_NAME"
      exit 1
    fi

    mkdir -p "$(dirname "$LOG_FILE")"

    printf -v ESCAPED_CMD '%q ' "$@"
    screen -L -Logfile "$LOG_FILE" -S "$SESSION_NAME" -dm bash -lc "$ESCAPED_CMD"
    echo "Started session: $SESSION_NAME"
    echo "Log file: $LOG_FILE"
    ;;

  status)
    if [ "$#" -ne 1 ]; then
      usage
      exit 1
    fi
    if has_session "$1"; then
      echo "running"
      exit 0
    fi
    echo "not-running"
    exit 1
    ;;

  attach)
    if [ "$#" -ne 1 ]; then
      usage
      exit 1
    fi
    exec screen -r "$1"
    ;;

  stop)
    if [ "$#" -ne 1 ]; then
      usage
      exit 1
    fi
    screen -S "$1" -X quit
    echo "Stopped session: $1"
    ;;

  list)
    screen -ls || true
    ;;

  *)
    usage
    exit 1
    ;;
esac
