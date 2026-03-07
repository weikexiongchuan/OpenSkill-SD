#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[3]
SSH_PASSWORD_EXEC = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_exec.sh"
SSH_PASSWORD_COPY = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_copy.sh"
TRAIN_STATE_RECORD = ROOT / "l3" / "lora-training-state-record-update" / "scripts" / "record_lora_training_state.py"

SDXL_TOKENIZER_REPOS = [
    "openai/clip-vit-large-patch14",
    "laion/CLIP-ViT-bigG-14-laion2B-39B-b160k",
]


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


def detect_tokenizer_repos(model_train_type: str) -> List[str]:
    if model_train_type in {"sdxl-lora", "sdxl-finetune"}:
        return SDXL_TOKENIZER_REPOS
    return []


def prefetch_tokenizers(login: Dict[str, str], state: Dict[str, str], repos: List[str], env: Dict[str, str]) -> None:
    if not repos:
        return
    repo_json = json.dumps(repos, ensure_ascii=False)
    remote_cmd = (
        "export HF_ENDPOINT=https://hf-mirror.com; "
        "if command -v python >/dev/null 2>&1; then PY=python; "
        "elif command -v python3 >/dev/null 2>&1; then PY=python3; "
        "else echo python-interpreter-not-found >&2; exit 127; fi; "
        "$PY - <<'PY'\n"
        "import json\n"
        "from huggingface_hub import snapshot_download\n"
        f"repos = json.loads({json.dumps(repo_json)})\n"
        "for repo in repos:\n"
        "    snapshot_download(repo_id=repo, allow_patterns=['*.json','*.txt','*.model','*.vocab','*.merges*','tokenizer*'], ignore_patterns=['*.safetensors','*.bin','*.onnx'])\n"
        "    print(f'prefetched:{repo}')\n"
        "PY"
    )
    output = run_remote_simple(login, state, remote_cmd, env)
    for line in clean_remote_output(output):
        if line.startswith("prefetched:"):
            print(line, flush=True)


def resolve_logging_dir(app_dir: str, config: dict) -> str:
    logging_dir = str(config.get("logging_dir") or "./logs")
    if logging_dir.startswith("/"):
        return logging_dir
    return str((Path(app_dir) / logging_dir).resolve())


def gather_remote_state(login: Dict[str, str], state: Dict[str, str], app_dir: str, logging_dir: str, env: Dict[str, str]) -> dict:
    marker = "__SDSKILL_JSON__"
    remote_cmd = (
        "if command -v python >/dev/null 2>&1; then PY=python; "
        "elif command -v python3 >/dev/null 2>&1; then PY=python3; "
        "else echo python-interpreter-not-found >&2; exit 127; fi; "
        f"APP_DIR={shlex.quote(app_dir)} LOG_DIR={shlex.quote(logging_dir)} $PY - <<'PY'\n"
        "import json, os\n"
        "from pathlib import Path\n"
        "app_dir = Path(os.environ['APP_DIR'])\n"
        "logging_dir = Path(os.environ['LOG_DIR'])\n"
        "logs = sorted((app_dir / 'logs').glob('lora-scripts-main-*.log'), key=lambda p: p.stat().st_mtime if p.exists() else 0)\n"
        "latest_log = logs[-1] if logs else None\n"
        "event_files = []\n"
        "if logging_dir.exists():\n"
        "    event_files = sorted(str(p) for p in logging_dir.rglob('events.out.tfevents*'))\n"
        "data = {\n"
        "  'latest_log': str(latest_log) if latest_log else '',\n"
        "  'latest_log_size': latest_log.stat().st_size if latest_log and latest_log.exists() else 0,\n"
        "  'event_files': event_files,\n"
        "}\n"
        f"print('{marker}')\n"
        "print(json.dumps(data, ensure_ascii=False))\n"
        "PY"
    )
    output = run_remote_simple(login, state, remote_cmd, env)
    lines = clean_remote_output(output)
    if marker not in lines:
        raise SystemExit(f"failed to gather remote state: {output}")
    index = lines.index(marker)
    return json.loads(lines[index + 1])


def remote_api_json(login: Dict[str, str], state: Dict[str, str], cmd: str, env: Dict[str, str]) -> dict:
    output = run_remote_simple(login, state, cmd, env)
    lines = clean_remote_output(output)
    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise SystemExit(f"failed to parse remote api json: {output}")


def extract_task_id(payload: dict) -> str:
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("id", "task_id", "uuid"):
            value = data.get(key)
            if value:
                return str(value)
    message = str(payload.get("message") or "")
    match = re.search(r"([0-9a-fA-F-]{8,})", message)
    return match.group(1) if match else ""


def read_remote_log_tail(login: Dict[str, str], state: Dict[str, str], log_path: str, offset: int, env: Dict[str, str]) -> str:
    if not log_path:
        return ""
    remote_cmd = (
        f"if [ -f {shlex.quote(log_path)} ]; then "
        f"tail -c +{max(offset + 1, 1)} {shlex.quote(log_path)}; "
        "fi"
    )
    return run_remote_simple(login, state, remote_cmd, env)


def print_status(prefix: str, payload: dict) -> None:
    print(f"{prefix} {json.dumps(payload, ensure_ascii=False)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Start one lora-scripts training task remotely and monitor startup health.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("prepared_config_file")
    parser.add_argument("run_name")
    parser.add_argument("template_id")
    parser.add_argument("scenario", choices=["style", "character", "outfit-accessory", "other"])
    parser.add_argument("--api-base-url", default="http://127.0.0.1:28000")
    parser.add_argument("--app-dir", default="/root/autodl-tmp/lora-scripts/app")
    parser.add_argument("--poll-interval", type=int, default=5)
    parser.add_argument("--startup-timeout", type=int, default=180)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    base = workspace_root / "servers" / args.server_alias
    state = parse_markdown_kv(base / "state.md")
    login = parse_markdown_kv(base / "login" / "method.md")
    env = os.environ.copy()

    prepared_path = Path(args.prepared_config_file).expanduser().resolve()
    config = json.loads(prepared_path.read_text(encoding="utf-8"))
    model_train_type = str(config.get("model_train_type") or "")
    output_name = str(config.get("output_name") or args.run_name)
    output_dir = str(config.get("output_dir") or (args.app_dir.rstrip('/') + '/output'))
    logging_dir = resolve_logging_dir(args.app_dir, config)

    run_checked(
        [
            sys.executable,
            str(TRAIN_STATE_RECORD),
            str(workspace_root),
            args.server_alias,
            args.run_name,
            args.template_id,
            args.scenario,
            model_train_type or "other",
            "queued",
            "",
            args.api_base_url,
            output_name,
            "",
            args.notes or "startup-queued",
            "--output-dir",
            output_dir,
        ]
    )

    tokenizers = detect_tokenizer_repos(model_train_type)
    if tokenizers:
        print(f"PREFETCH {','.join(tokenizers)}", flush=True)
        prefetch_tokenizers(login, state, tokenizers, env)

    remote_cfg_dir = "/root/autodl-tmp/workspace/.skill-tmp/lora-training-configs"
    remote_prompt_dir = f"{remote_cfg_dir}/sample-prompts"
    remote_cfg = f"{remote_cfg_dir}/{prepared_path.name}"
    run_remote_simple(login, state, f"mkdir -p {shlex.quote(remote_cfg_dir)} {shlex.quote(remote_prompt_dir)} {shlex.quote(args.app_dir + '/config/autosave')} {shlex.quote(args.app_dir + '/logs')}", env)

    local_upload_path = prepared_path
    temp_config_path = None
    prompt_file_value = str(config.get("prompt_file") or "").strip()
    if prompt_file_value:
        prompt_candidate = Path(prompt_file_value).expanduser()
        if not prompt_candidate.is_absolute():
            prompt_candidate = (prepared_path.parent / prompt_candidate).resolve()
        if prompt_candidate.exists() and prompt_candidate.is_file():
            remote_prompt_path = f"{remote_prompt_dir}/{prompt_candidate.name}"
            copy_remote_file(login, state, prompt_candidate, remote_prompt_path, env)
            config["prompt_file"] = remote_prompt_path
            handle = tempfile.NamedTemporaryFile('w', suffix='.json', prefix='prepared-with-prompts-', delete=False, encoding='utf-8')
            temp_config_path = Path(handle.name)
            handle.write(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
            handle.close()
            local_upload_path = temp_config_path

    copy_remote_file(login, state, local_upload_path, remote_cfg, env)
    if temp_config_path is not None and temp_config_path.exists():
        temp_config_path.unlink(missing_ok=True)

    baseline = gather_remote_state(login, state, args.app_dir, logging_dir, env)
    baseline_events = set(baseline.get("event_files") or [])
    baseline_log_size = int(baseline.get("latest_log_size") or 0)
    latest_log_path = str(baseline.get("latest_log") or "")

    start_cmd = f"curl -sS -H 'Content-Type: application/json' --data @{shlex.quote(remote_cfg)} {shlex.quote(args.api_base_url + '/api/run')}"
    start_payload = remote_api_json(login, state, start_cmd, env)
    print_status("START", start_payload)
    task_id = extract_task_id(start_payload)
    if str(start_payload.get("status")) != "success":
        run_checked(
            [
                sys.executable,
                str(TRAIN_STATE_RECORD),
                str(workspace_root),
                args.server_alias,
                args.run_name,
                args.template_id,
                args.scenario,
                model_train_type or "other",
                "failed",
                task_id,
                args.api_base_url,
                output_name,
                "",
                args.notes or "api-start-failed",
                "--output-dir",
                output_dir,
            ]
        )
        return 1

    deadline = time.time() + args.startup_timeout
    confirmed_running = False
    while time.time() < deadline:
        tasks_payload = remote_api_json(login, state, f"curl -sS {shlex.quote(args.api_base_url + '/api/tasks')}", env)
        print_status("TASKS", tasks_payload)
        tasks = (((tasks_payload.get("data") or {}).get("tasks")) or []) if isinstance(tasks_payload, dict) else []
        current = None
        if task_id:
            for item in tasks:
                if str(item.get("id") or item.get("task_id") or item.get("uuid") or "") == task_id:
                    current = item
                    break
        elif tasks:
            current = tasks[0]
            task_id = str(current.get("id") or current.get("task_id") or current.get("uuid") or "")
        status = str((current or {}).get("status") or "")

        current_state = gather_remote_state(login, state, args.app_dir, logging_dir, env)
        current_events = set(current_state.get("event_files") or [])
        new_events = sorted(current_events - baseline_events)
        if new_events:
            print(f"EVENT {new_events[0]}", flush=True)
        tail = read_remote_log_tail(login, state, latest_log_path or str(current_state.get("latest_log") or ""), baseline_log_size, env)
        tail_text = "\n".join(clean_remote_output(tail))
        if tail_text:
            clipped = tail_text[-3000:]
            print(f"LOGTAIL {clipped}", flush=True)
            if any(token in clipped for token in ["Training failed", "Traceback", "OSError:", "RuntimeError:", "ModuleNotFoundError:"]):
                run_checked(
                    [
                        sys.executable,
                        str(TRAIN_STATE_RECORD),
                        str(workspace_root),
                        args.server_alias,
                        args.run_name,
                        args.template_id,
                        args.scenario,
                        model_train_type or "other",
                        "failed",
                        task_id,
                        args.api_base_url,
                        output_name,
                        "",
                        args.notes or "startup-log-failed",
                        "--output-dir",
                        output_dir,
                    ]
                )
                return 2

        if status == "RUNNING" and new_events:
            confirmed_running = True
            break
        if status == "FINISHED":
            run_checked(
                [
                    sys.executable,
                    str(TRAIN_STATE_RECORD),
                    str(workspace_root),
                    args.server_alias,
                    args.run_name,
                    args.template_id,
                    args.scenario,
                    model_train_type or "other",
                    "failed",
                    task_id,
                    args.api_base_url,
                    output_name,
                    "",
                    args.notes or "finished-before-events",
                    "--output-dir",
                    output_dir,
                ]
            )
            return 3
        time.sleep(args.poll_interval)

    if not confirmed_running:
        run_checked(
            [
                sys.executable,
                str(TRAIN_STATE_RECORD),
                str(workspace_root),
                args.server_alias,
                args.run_name,
                args.template_id,
                args.scenario,
                model_train_type or "other",
                "failed",
                task_id,
                args.api_base_url,
                output_name,
                "",
                args.notes or "startup-timeout",
                "--output-dir",
                output_dir,
            ]
        )
        return 4

    run_checked(
        [
            sys.executable,
            str(TRAIN_STATE_RECORD),
            str(workspace_root),
            args.server_alias,
            args.run_name,
            args.template_id,
            args.scenario,
            model_train_type or "other",
            "running",
            task_id,
            args.api_base_url,
            output_name,
            "",
            args.notes or "startup-confirmed",
            "--output-dir",
            output_dir,
        ]
    )
    print(f"CONFIRMED task_id={task_id} output={output_name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
