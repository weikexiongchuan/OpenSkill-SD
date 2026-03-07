#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 -- <command...>"
}

if [ "$#" -lt 2 ]; then
  usage
  exit 1
fi

if [ "$1" != "--" ]; then
  usage
  exit 1
fi
shift

if [ ! -f /etc/network_turbo ]; then
  echo "/etc/network_turbo not found"
  exit 1
fi

printf -v CMD_ESCAPED '%q ' "$@"
exec bash -lc "source /etc/network_turbo && $CMD_ESCAPED"
