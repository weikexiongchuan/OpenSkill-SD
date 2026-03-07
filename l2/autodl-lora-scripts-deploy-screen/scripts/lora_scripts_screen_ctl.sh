#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  $0 start <install-dir> <session-name> [-- <extra-args...>]
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

resolve_python() {
  if [ -n "${LORA_SCRIPTS_PYTHON:-}" ] && [ -x "${LORA_SCRIPTS_PYTHON}" ]; then
    echo "${LORA_SCRIPTS_PYTHON}"
    return 0
  fi
  if [ -x /root/miniconda3/bin/python ]; then
    echo "/root/miniconda3/bin/python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}

has_session() {
  local name="$1"
  screen -ls 2>/dev/null | grep -q "[.]${name}[[:space:]]"
}

case "$ACTION" in
  start)
    if [ "$#" -lt 2 ]; then
      usage
      exit 1
    fi

    INSTALL_DIR="$1"
    SESSION_NAME="$2"
    shift 2

    PORT="${LORA_SCRIPTS_PORT:-28000}"
    TENSORBOARD_PORT="${LORA_SCRIPTS_TENSORBOARD_PORT:-6016}"
    DISABLE_TENSORBOARD="${LORA_SCRIPTS_DISABLE_TENSORBOARD:-0}"
    DISABLE_TAGEDITOR="${LORA_SCRIPTS_DISABLE_TAGEDITOR:-0}"

    EXTRA_ARGS=()
    if [ "$#" -gt 0 ]; then
      if [ "$1" != "--" ]; then
        echo "If extra args are provided, prepend with --"
        exit 1
      fi
      shift
      EXTRA_ARGS=("$@")
    fi

    if [ ! -f "$INSTALL_DIR/gui.py" ]; then
      echo "lora-scripts gui.py not found in $INSTALL_DIR"
      exit 1
    fi

    PY_BIN="$(resolve_python || true)"
    if [ -z "$PY_BIN" ]; then
      echo "No usable python found. Set LORA_SCRIPTS_PYTHON to a valid interpreter."
      exit 1
    fi

    if ! "$PY_BIN" -c 'import pkg_resources' >/dev/null 2>&1; then
      echo "pkg_resources missing; installing compatible setuptools"
      "$PY_BIN" -m pip install 'setuptools<81'
    fi

    if has_session "$SESSION_NAME"; then
      echo "Session already running: $SESSION_NAME"
      exit 1
    fi

    LOG_DIR="$INSTALL_DIR/logs"
    AUTOSAVE_DIR="$INSTALL_DIR/config/autosave"
    MODEL_DIR="$INSTALL_DIR/sd-models"
    mkdir -p "$LOG_DIR" "$AUTOSAVE_DIR" "$MODEL_DIR"
    LOG_FILE="$LOG_DIR/${SESSION_NAME}-$(date +%Y%m%d-%H%M%S).log"

    CMD=("$PY_BIN" gui.py --listen --port "$PORT" --skip-prepare-environment --tensorboard-port "$TENSORBOARD_PORT")
    if [ "$DISABLE_TENSORBOARD" = "1" ]; then
      CMD+=(--disable-tensorboard)
    fi
    if [ "$DISABLE_TAGEDITOR" = "1" ]; then
      CMD+=(--disable-tageditor)
    fi
    if [ "${#EXTRA_ARGS[@]}" -gt 0 ]; then
      CMD+=("${EXTRA_ARGS[@]}")
    fi

    printf -v CMD_ESCAPED '%q ' "${CMD[@]}"

    screen -L -Logfile "$LOG_FILE" -S "$SESSION_NAME" -dm bash -lc \
      "cd \"$INSTALL_DIR\" && $CMD_ESCAPED"

    echo "Started lora-scripts session: $SESSION_NAME"
    echo "Python: $PY_BIN"
    echo "Listen: 0.0.0.0:$PORT"
    echo "Tensorboard port: $TENSORBOARD_PORT"
    echo "Log file: $LOG_FILE"
    ;;

  status)
    if [ "$#" -ne 1 ]; then
      usage
      exit 1
    fi
    if has_session "$1"; then
      echo "running"
    else
      echo "not-running"
      exit 1
    fi
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
