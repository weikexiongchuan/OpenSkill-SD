#!/usr/bin/env bash
set -euo pipefail

if [ -f /etc/network_turbo ]; then
  echo "network_turbo=available"
  bash -lc 'source /etc/network_turbo && env | grep -Ei "^(http|https|all|HTTP|HTTPS|ALL)_proxy=|^(no|NO)_proxy=" || true'
  exit 0
fi

echo "network_turbo=missing"
exit 1
