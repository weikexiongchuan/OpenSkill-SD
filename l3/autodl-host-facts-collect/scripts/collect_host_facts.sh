#!/usr/bin/env bash
set -euo pipefail

OUT_FILE="${1:-host-facts-$(date +%Y%m%d-%H%M%S).log}"

{
  echo "# Host Facts"
  echo "timestamp=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "user=$(whoami)"
  echo

  echo "## OS"
  uname -a || true
  if [ -f /etc/os-release ]; then
    cat /etc/os-release
  fi
  echo

  echo "## GPU"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi -L || true
    nvidia-smi || true
  else
    echo "nvidia-smi not found"
  fi
  echo

  echo "## Storage: lsblk -f"
  lsblk -f || true
  echo

  echo "## Storage: df -hT"
  df -hT || true
  echo

  echo "## Mounts"
  mount | sort || true
  echo

  echo "## Screen Sessions"
  if command -v screen >/dev/null 2>&1; then
    screen -ls || true
  else
    echo "screen not found"
  fi
} > "$OUT_FILE"

echo "Wrote host facts to: $OUT_FILE"
