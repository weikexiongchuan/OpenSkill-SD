#!/usr/bin/env bash
set -euo pipefail

env | grep -Ei '^(http|https|all|HTTP|HTTPS|ALL)_proxy=|^(no|NO)_proxy=' || true
