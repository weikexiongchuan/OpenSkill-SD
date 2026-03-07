#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[3]
REMOTE_WORKER = ROOT / "l3" / "lora-training-dataset-prepare" / "scripts" / "remote_prepare_lora_dataset.py"
RECORD_SCRIPT = ROOT / "l3" / "lora-training-dataset-prepare" / "scripts" / "record_lora_dataset.py"
SSH_PASSWORD_EXEC = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_exec.sh"
SSH_PASSWORD_COPY = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_copy.sh"


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or "dataset"


def parse_markdown_kv(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            data[key.strip()] = value.strip()
    return data


def clean_remote_output(text: str) -> List[str]:
    lines: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("spawn ssh"):
            continue
        if line.endswith("password:"):
            continue
        lines.append(line)
    return lines


def run_checked(cmd: List[str], env: Dict[str, str] | None = None) -> str:
    result = subprocess.run(cmd, text=True, capture_output=True, env=env)
    if result.returncode != 0:
        raise SystemExit(result.stdout + result.stderr)
    return result.stdout


def build_remote_python_command(script_path: str, *script_args: str) -> str:
    joined_args = " ".join(shlex.quote(arg) for arg in script_args)
    return (
        "if command -v python >/dev/null 2>&1; then PY=python; "
        "elif command -v python3 >/dev/null 2>&1; then PY=python3; "
        "else echo 'python interpreter not found on remote host' >&2; exit 127; fi; "
        "$PY -c 'import importlib.util, subprocess, sys; "
        "importlib.util.find_spec(\"PIL\") or subprocess.check_call([sys.executable, \"-m\", \"pip\", \"install\", \"--user\", \"Pillow\"])'; "
        f"$PY -u {shlex.quote(script_path)} {joined_args}".strip()
    )


def wrap_remote_login_shell(remote_cmd: str) -> List[str]:
    return ["bash", "-lc", remote_cmd]


def build_key_ssh_command(host: str, port: str, user: str, identity_file: str, remote_cmd: str) -> List[str]:
    cmd = ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-p", port]
    if identity_file:
        cmd.extend(["-i", identity_file])
    cmd.append(f"{user}@{host}")
    cmd.extend(wrap_remote_login_shell(remote_cmd))
    return cmd


def run_remote_simple(login: Dict[str, str], state: Dict[str, str], remote_cmd: str, env: Dict[str, str]) -> str:
    host = state["Host"]
    port = state["Port"]
    user = state["User"]
    method = login.get("Method", "")
    identity_file = login.get("Identity File", "")
    if method == "key":
        output = run_checked(build_key_ssh_command(host, port, user, identity_file, remote_cmd), env=env)
        return "\n".join(clean_remote_output(output))
    if method == "password":
        wrapped = " ".join(shlex.quote(part) for part in wrap_remote_login_shell(remote_cmd))
        command = f"{shlex.quote(str(SSH_PASSWORD_EXEC))} {shlex.quote(host)} {shlex.quote(port)} {shlex.quote(user)} -- {wrapped}"
        output = run_checked(["bash", "-lc", command], env=env)
        return "\n".join(clean_remote_output(output))
    raise SystemExit(f"unsupported login method: {method}")


def copy_remote_file(login: Dict[str, str], state: Dict[str, str], local_path: Path, remote_path: str, env: Dict[str, str]) -> None:
    host = state["Host"]
    port = state["Port"]
    user = state["User"]
    method = login.get("Method", "")
    identity_file = login.get("Identity File", "")
    if method == "key":
        cmd = ["scp", "-P", port, "-r"]
        if identity_file:
            cmd.extend(["-i", identity_file])
        cmd.extend([str(local_path), f"{user}@{host}:{remote_path}"])
        run_checked(cmd, env=env)
        return
    if method == "password":
        command = f"{shlex.quote(str(SSH_PASSWORD_COPY))} {shlex.quote(str(local_path))} {shlex.quote(host)} {shlex.quote(port)} {shlex.quote(user)} {shlex.quote(remote_path)}"
        run_checked(["bash", "-lc", command], env=env)
        return
    raise SystemExit(f"unsupported login method: {method}")


def detect_tier(path: str) -> str:
    if path.startswith("/autodl-fs/"):
        return "fs"
    if path.startswith("/root/autodl-tmp/"):
        return "tmp"
    if "/pub" in path or path.startswith("/autodl-pub/"):
        return "pub"
    return "other"


def extract_json_line(text: str) -> Dict[str, object]:
    lines = clean_remote_output(text)
    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise SystemExit(f"failed to parse remote dataset summary from output:\n{text}")


def remote_path_exists(login: Dict[str, str], state: Dict[str, str], path: str, env: Dict[str, str]) -> bool:
    output = run_remote_simple(login, state, f"if [ -e {shlex.quote(path)} ]; then echo yes; else echo no; fi", env)
    return output.strip().endswith("yes")


def determine_source_mode(raw_source: str, requested: str) -> str:
    if requested != "auto":
        return requested
    local_candidate = Path(raw_source).expanduser()
    if local_candidate.exists():
        return "local"
    if raw_source.startswith("/"):
        return "remote"
    raise SystemExit("cannot infer dataset source mode; use --source-mode local or --source-mode remote")


def status_exit_code(status: str) -> int:
    if status in {"ready", "prepared"}:
        return 0
    if status == "needs-captions":
        return 2
    if status == "needs-size-fix":
        return 3
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload/check/fix one LoRA training dataset on the current server.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("dataset_source")
    parser.add_argument("dataset_name", nargs="?", default="")
    parser.add_argument("--source-mode", choices=["auto", "local", "remote"], default="auto")
    parser.add_argument("--remote-root", default="/autodl-fs/data/datasets")
    parser.add_argument("--remote-path", default="")
    parser.add_argument("--size-policy", choices=["crop", "pad-white", "check-only"], default="crop")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    base = workspace_root / "servers" / args.server_alias
    state = parse_markdown_kv(base / "state.md")
    login = parse_markdown_kv(base / "login" / "method.md")
    remote_workspace_root = state.get("Workspace Root", "") or "/root/autodl-tmp/workspace"
    env = os.environ.copy()

    source_mode = determine_source_mode(args.dataset_source, args.source_mode)
    source_label = "remote-existing"
    dataset_label = args.dataset_name.strip() if args.dataset_name else ""

    if source_mode == "local":
        local_source = Path(args.dataset_source).expanduser().resolve()
        if not local_source.exists() or not local_source.is_dir():
            raise SystemExit(f"local dataset directory not found: {local_source}")
        dataset_label = dataset_label or local_source.name
        remote_target = args.remote_path or f"{args.remote_root.rstrip('/')}/{slugify(dataset_label)}"
        parent_dir = str(Path(remote_target).parent)
        run_remote_simple(login, state, f"mkdir -p {shlex.quote(parent_dir)}", env)
        if remote_path_exists(login, state, remote_target, env):
            remote_target = f"{remote_target.rstrip('/')}-{now_stamp()}"
        copy_remote_file(login, state, local_source, remote_target, env)
        source_label = "local-upload"
    else:
        remote_target = args.remote_path or args.dataset_source
        if not remote_target.startswith("/"):
            raise SystemExit("remote dataset path must be an absolute path")
        dataset_label = dataset_label or Path(remote_target).name or "dataset"
        if not remote_path_exists(login, state, remote_target, env):
            raise SystemExit(f"remote dataset directory not found: {remote_target}")

    runtime_output_dir = args.output_dir or ""
    remote_tmp_dir = f"{remote_workspace_root}/.skill-tmp/lora-training-dataset-prepare"
    remote_worker_path = f"{remote_tmp_dir}/remote_prepare_lora_dataset.py"
    run_remote_simple(login, state, f"mkdir -p {shlex.quote(remote_tmp_dir)}", env)
    copy_remote_file(login, state, REMOTE_WORKER, remote_worker_path, env)

    worker_cmd = build_remote_python_command(
        remote_worker_path,
        remote_target,
        "--size-policy",
        args.size_policy,
        *( ["--output-dir", runtime_output_dir] if runtime_output_dir else [] ),
    )
    output = run_remote_simple(login, state, worker_cmd, env)
    summary = extract_json_line(output)

    dataset_id = slugify(dataset_label)
    stored_path = remote_target
    runtime_path = str(summary.get("runtime_dir") or remote_target)
    storage_tier = detect_tier(stored_path)

    run_checked(
        [
            sys.executable,
            str(RECORD_SCRIPT),
            str(workspace_root),
            args.server_alias,
            dataset_id,
            dataset_label,
            source_label,
            storage_tier,
            stored_path,
            runtime_path,
            str(summary.get("status") or "unknown"),
            args.size_policy,
            json.dumps(summary, ensure_ascii=False, separators=(",", ":")),
            args.notes,
        ]
    )

    print(f"DATASET {dataset_label}")
    print(f"SOURCE {source_label}")
    print(f"STORED {stored_path}")
    print(f"RUNTIME {runtime_path}")
    print(f"STATUS {summary.get('status')}")
    print(
        "COUNTS "
        f"images={summary.get('image_count', 0)} "
        f"paired={summary.get('paired_count', 0)} "
        f"missing={summary.get('missing_caption_count', 0)} "
        f"orphan={summary.get('orphan_caption_count', 0)} "
        f"resized={summary.get('resized_count', 0)} "
        f"resize_errors={summary.get('resize_error_count', 0)}"
    )
    issues = summary.get("sample_issues") or []
    if issues:
        print("ISSUES")
        for item in issues:
            print(f"- {item}")
    return status_exit_code(str(summary.get("status") or "unknown"))


if __name__ == "__main__":
    raise SystemExit(main())
