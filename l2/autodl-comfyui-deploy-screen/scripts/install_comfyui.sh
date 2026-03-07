#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <install-dir> [repo-url] [branch]"
  exit 1
fi

INSTALL_DIR="$1"
REPO_URL="${2:-https://github.com/comfyanonymous/ComfyUI.git}"
BRANCH="${3:-master}"

resolve_python() {
  if [ -n "${COMFYUI_PYTHON:-}" ] && [ -x "${COMFYUI_PYTHON}" ]; then
    echo "${COMFYUI_PYTHON}"
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
  echo "Updating existing ComfyUI repo: $INSTALL_DIR"
  git -C "$INSTALL_DIR" fetch --all --tags
  git -C "$INSTALL_DIR" checkout "$BRANCH"
  git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
else
  echo "Cloning ComfyUI into: $INSTALL_DIR"
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

PY_BIN="$(resolve_python || true)"
if [ -z "$PY_BIN" ]; then
  echo "No usable python found. Set COMFYUI_PYTHON to a valid interpreter."
  exit 1
fi

"$PY_BIN" -m pip install --upgrade pip wheel setuptools
"$PY_BIN" -m pip install -r "$INSTALL_DIR/requirements.txt"

echo "Using python: $PY_BIN"
echo "ComfyUI install complete: $INSTALL_DIR"
