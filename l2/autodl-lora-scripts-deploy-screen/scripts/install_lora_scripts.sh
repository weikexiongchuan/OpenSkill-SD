#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <install-dir> [repo-url] [branch]"
  exit 1
fi

INSTALL_DIR="$1"
REPO_URL="${2:-https://github.com/Akegarasu/lora-scripts.git}"
BRANCH="${3:-main}"

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

if [ -f "./.proxy_env" ]; then
  # shellcheck source=/dev/null
  source "./.proxy_env"
fi

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Updating existing lora-scripts repo: $INSTALL_DIR"
  git -C "$INSTALL_DIR" fetch --all --tags
  git -C "$INSTALL_DIR" checkout "$BRANCH"
  git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
else
  echo "Cloning lora-scripts into: $INSTALL_DIR"
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

git -C "$INSTALL_DIR" submodule update --init --recursive

PY_BIN="$(resolve_python || true)"
if [ -z "$PY_BIN" ]; then
  echo "No usable python found. Set LORA_SCRIPTS_PYTHON to a valid interpreter."
  exit 1
fi

export PATH="$(dirname "$PY_BIN"):$PATH"
"$PY_BIN" -m pip install --upgrade pip wheel
"$PY_BIN" -m pip install 'setuptools<81'
bash "$INSTALL_DIR/install.bash" --disable-venv
"$PY_BIN" - <<'PY'
import sys
try:
    import pkg_resources  # noqa:F401
except Exception:
    raise SystemExit("pkg_resources is still unavailable after install")
print("pkg_resources-ok")
PY

echo "Using python: $PY_BIN"
echo "lora-scripts install complete: $INSTALL_DIR"
