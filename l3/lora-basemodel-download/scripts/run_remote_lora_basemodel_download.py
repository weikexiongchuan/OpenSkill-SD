#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
RESOLVE_SCRIPT = ROOT / "l3" / "lora-basemodel-download" / "scripts" / "resolve_lora_basemodel_download.py"
RECORD_SCRIPT = ROOT / "l3" / "lora-basemodel-download" / "scripts" / "record_lora_basemodel.py"
REMOTE_WORKER = ROOT / "l3" / "lora-basemodel-download" / "scripts" / "remote_hf_file_download.py"
SSH_PASSWORD_EXEC = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_exec.sh"
SSH_PASSWORD_COPY = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_copy.sh"
MARKER = "__SDSKILL_STATUS__"


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
    python_cmd = f"python -u {shlex.quote(script_path)} {joined_args}".strip()
    python3_cmd = f"python3 -u {shlex.quote(script_path)} {joined_args}".strip()
    return (
        "if command -v python >/dev/null 2>&1; then "
        f"{python_cmd}; "
        "elif command -v python3 >/dev/null 2>&1; then "
        f"{python3_cmd}; "
        "else echo '{\"event\":\"error\",\"message\":\"python interpreter not found on remote host\"}'; exit 127; fi"
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
        cmd = ["scp", "-P", port]
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


def parse_pid(output: str) -> str:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.isdigit():
            return line
    raise SystemExit(f"failed to parse remote pid from output: {output}")


def parse_poll_output(output: str) -> Tuple[List[str], str, int]:
    lines = output.splitlines()
    if MARKER not in lines:
        return lines, "unknown", 0
    idx = lines.index(MARKER)
    event_lines = lines[:idx]
    state = lines[idx + 1].strip() if idx + 1 < len(lines) else "unknown"
    current_size = 0
    if idx + 2 < len(lines):
        try:
            current_size = int(lines[idx + 2].strip())
        except ValueError:
            current_size = 0
    return event_lines, state, current_size


def format_event(event: Dict[str, object]) -> str:
    kind = str(event.get("event", ""))
    if kind == "size":
        return f"SIZE {event['human']}"
    if kind == "start":
        return f"START 已有 {event['existing_human']}"
    if kind == "warmup":
        return f"WARMUP 均速 {event['average_speed_human']} 预计剩余 {event['eta_seconds']} 秒"
    if kind == "progress":
        return (
            f"PROGRESS {event['percent']}% {event['downloaded_human']}/{event['total_human']} "
            f"当前 {event['current_speed_human']} 均速 {event['average_speed_human']} ETA {event['eta_seconds']} 秒"
        )
    if kind == "done":
        return f"DONE {event['downloaded_human']} 用时 {event['elapsed_seconds']} 秒 均速 {event['average_speed_human']}"
    if kind == "error":
        return f"ERROR {event['message']}"
    return json.dumps(event, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one remote LoRA basemodel download through the current server workspace.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("family")
    parser.add_argument("version", nargs="?", default="")
    parser.add_argument("branch", nargs="?", default="")
    parser.add_argument("--storage-root", default="/autodl-fs/data/models")
    parser.add_argument("--runtime-link-root", default="/root/autodl-tmp/lora-scripts/app/sd-models")
    parser.add_argument("--activation-mode", choices=["link", "copy", "none"], default="link")
    parser.add_argument("--filename-override", default="")
    parser.add_argument("--warmup-seconds", type=int, default=6)
    parser.add_argument("--report-interval", type=int, default=15)
    parser.add_argument("--poll-interval", type=int, default=5)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    base = workspace_root / "servers" / args.server_alias
    state = parse_markdown_kv(base / "state.md")
    login = parse_markdown_kv(base / "login" / "method.md")
    remote_workspace_root = state.get("Workspace Root", "") or "/root/autodl-tmp/workspace"
    env = os.environ.copy()

    resolved = json.loads(
        run_checked(
            [
                sys.executable,
                str(RESOLVE_SCRIPT),
                args.family,
                args.version,
                args.branch,
                "--storage-root",
                args.storage_root,
                "--runtime-link-root",
                args.runtime_link_root,
                "--activation-mode",
                args.activation_mode,
                "--filename-override",
                args.filename_override,
            ]
        )
    )

    storage_tier = "fs" if resolved["stored_path"].startswith("/autodl-fs/") else "tmp"
    run_checked(
        [
            sys.executable,
            str(RECORD_SCRIPT),
            str(workspace_root),
            args.server_alias,
            resolved["slot_id"],
            resolved["label"],
            resolved["family"],
            resolved["family_version"],
            resolved["family_branch"],
            resolved["repo_id"],
            resolved["filename"],
            resolved["download_mode"],
            storage_tier,
            resolved["stored_path"],
            resolved["runtime_path"],
            "planned",
            args.notes or "remote-download-planned",
        ]
    )

    remote_tmp_dir = f"{remote_workspace_root}/.skill-tmp/lora-basemodel-download"
    remote_worker_path = f"{remote_tmp_dir}/remote_hf_file_download.py"
    run_id = str(int(time.time()))
    remote_status_path = f"{remote_tmp_dir}/{resolved['slot_id']}__{run_id}.status.jsonl"
    remote_log_path = f"{remote_tmp_dir}/{resolved['slot_id']}__{run_id}.log"
    run_remote_simple(login, state, f"mkdir -p {shlex.quote(remote_tmp_dir)}", env)
    copy_remote_file(login, state, REMOTE_WORKER, remote_worker_path, env)

    mirror_url = f"https://hf-mirror.com/{resolved['repo_id']}/resolve/main/{resolved['filename']}"
    worker_cmd = build_remote_python_command(
        remote_worker_path,
        mirror_url,
        resolved["stored_path"],
        "--warmup-seconds",
        str(args.warmup_seconds),
        "--report-interval",
        str(args.report_interval),
        "--status-file",
        remote_status_path,
    )
    start_cmd = (
        f"rm -f {shlex.quote(remote_status_path)} {shlex.quote(remote_log_path)}; "
        f"nohup bash -lc {shlex.quote(worker_cmd)} >> {shlex.quote(remote_log_path)} 2>&1 < /dev/null & echo $!"
    )
    pid = parse_pid(run_remote_simple(login, state, start_cmd, env))
    print(f"PID {pid}", flush=True)

    seen_lines = 0
    terminal_event = ""
    terminal_message = ""
    while True:
        poll_cmd = (
            f"if [ -f {shlex.quote(remote_status_path)} ]; then tail -n +{seen_lines + 1} {shlex.quote(remote_status_path)}; fi; "
            f"echo {MARKER}; "
            f"if kill -0 {pid} 2>/dev/null; then echo RUNNING; else echo STOPPED; fi; "
            f"if [ -f {shlex.quote(resolved['stored_path'] + '.part')} ]; then stat -c %s {shlex.quote(resolved['stored_path'] + '.part')}; "
            f"elif [ -f {shlex.quote(resolved['stored_path'])} ]; then stat -c %s {shlex.quote(resolved['stored_path'])}; else echo 0; fi"
        )
        event_lines, process_state, current_size = parse_poll_output(run_remote_simple(login, state, poll_cmd, env))
        for line in event_lines:
            if not line.strip():
                continue
            seen_lines += 1
            event = json.loads(line)
            print(format_event(event), flush=True)
            if event.get("event") in {"done", "error"}:
                terminal_event = str(event.get("event"))
                terminal_message = str(event.get("message", ""))
        if terminal_event:
            break
        if process_state != "RUNNING":
            break
        if current_size > 0 and seen_lines == 0:
            print(f"PROGRESS 已落盘 {current_size} 字节", flush=True)
        time.sleep(args.poll_interval)

    if terminal_event == "error":
        run_checked(
            [
                sys.executable,
                str(RECORD_SCRIPT),
                str(workspace_root),
                args.server_alias,
                resolved["slot_id"],
                resolved["label"],
                resolved["family"],
                resolved["family_version"],
                resolved["family_branch"],
                resolved["repo_id"],
                resolved["filename"],
                resolved["download_mode"],
                storage_tier,
                resolved["stored_path"],
                resolved["runtime_path"],
                "failed",
                terminal_message or args.notes or "remote-download-failed",
            ]
        )
        return 1

    if terminal_event != "done":
        run_checked(
            [
                sys.executable,
                str(RECORD_SCRIPT),
                str(workspace_root),
                args.server_alias,
                resolved["slot_id"],
                resolved["label"],
                resolved["family"],
                resolved["family_version"],
                resolved["family_branch"],
                resolved["repo_id"],
                resolved["filename"],
                resolved["download_mode"],
                storage_tier,
                resolved["stored_path"],
                resolved["runtime_path"],
                "failed",
                args.notes or "remote-download-stopped-without-terminal-event",
            ]
        )
        raise SystemExit("remote download stopped without a done/error event")

    final_status = "downloaded"
    if resolved["activate_command"]:
        run_remote_simple(login, state, resolved["activate_command"], env)
        final_status = "linked" if args.activation_mode == "link" else "downloaded"

    run_checked(
        [
            sys.executable,
            str(RECORD_SCRIPT),
            str(workspace_root),
            args.server_alias,
            resolved["slot_id"],
            resolved["label"],
            resolved["family"],
            resolved["family_version"],
            resolved["family_branch"],
            resolved["repo_id"],
            resolved["filename"],
            resolved["download_mode"],
            storage_tier,
            resolved["stored_path"],
            resolved["runtime_path"],
            final_status,
            args.notes or "remote-download-finished",
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
