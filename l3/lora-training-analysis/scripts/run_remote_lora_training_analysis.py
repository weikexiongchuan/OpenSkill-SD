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
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
SSH_PASSWORD_EXEC = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_exec.sh"
ANSI_RE = re.compile(r"\x1B(?:\[[0-?]*[ -/]*[@-~]|\].*?(?:\x07|\x1b\\)|[@-Z\\-_])")
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?$")
RANGE_RE = re.compile(r"^\s*[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?\s*~")
PROGRESS_RE = re.compile(r"steps:\s*(\d+)/(\d+).*?avr_loss=([0-9.]+)")
TASK_ID_RE = re.compile(r"([0-9a-fA-F-]{8,})")

ERROR_PATTERNS: List[Tuple[re.Pattern[str], str, str, str]] = [
    (re.compile(r"Can't load tokenizer", re.I), "high", "缺少 tokenizer 依赖", "先补齐 SDXL 相关 tokenizer，再重新启动训练。"),
    (re.compile(r"TypeError: '<=' not supported between instances of 'float' and 'str'", re.I), "high", "配置里的数值仍是字符串", "先把学习率、epoch、batch 等字段归一化为真正数值，再重新启动。"),
    (re.compile(r"CUDA out of memory", re.I), "high", "显存不足", "降低分辨率、batch、network_dim，或减少同时训练的模块。"),
    (re.compile(r"No space left on device", re.I), "high", "磁盘空间不足", "清理输出或把大文件迁到文件存储，再继续训练。"),
    (re.compile(r"ModuleNotFoundError|ImportError", re.I), "high", "运行环境依赖缺失", "先补齐缺失依赖，再重新启动训练。"),
    (re.compile(r"Traceback \(most recent call last\)", re.I), "high", "训练日志出现 traceback", "优先按 traceback 首个报错定位根因。"),
    (re.compile(r"Training failed|训练失败", re.I), "high", "训练已经失败", "先定位失败前最后一个明确错误，再决定是否重跑。"),
]

NUMERIC_KEYS = {
    "learning_rate",
    "unet_lr",
    "text_encoder_lr",
    "max_train_epochs",
    "train_batch_size",
    "network_dim",
    "network_alpha",
    "save_every_n_epochs",
    "gradient_accumulation_steps",
    "lr_warmup_steps",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sanitize(text: str) -> str:
    value = ANSI_RE.sub("", text or "")
    value = value.replace("\r", "\n")
    return value


def sanitize_inline(text: str) -> str:
    return (text or "").replace("|", "/").replace("\n", " ").strip()


def parse_markdown_kv(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            data[key.strip()] = value.strip()
    return data


def load_history_lines(path: Path, marker: str) -> List[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    if marker not in content:
        return []
    block = content.split(marker, 1)[1]
    return [line for line in block.splitlines() if line.startswith("- ")]


def resolve_rel(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path)


def run_checked(cmd: List[str], env: Dict[str, str] | None = None) -> str:
    result = subprocess.run(cmd, text=True, capture_output=True, env=env)
    if result.returncode != 0:
        raise RuntimeError((result.stdout + result.stderr).strip() or f"command failed: {' '.join(cmd)}")
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


def clean_remote_output(text: str) -> List[str]:
    lines: List[str] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("spawn ssh"):
            continue
        if line.endswith("password:"):
            continue
        lines.append(line)
    return lines


def run_remote_simple(login: Dict[str, str], state: Dict[str, str], remote_cmd: str, env: Dict[str, str]) -> str:
    host = state.get("Host", "")
    port = state.get("Port", "")
    user = state.get("User", "")
    method = login.get("Method", "")
    identity_file = login.get("Identity File", "")
    if not host or not port or not user:
        raise RuntimeError("remote state is incomplete")
    if method == "key":
        output = run_checked(build_key_ssh_command(host, port, user, identity_file, remote_cmd), env=env)
        return "\n".join(clean_remote_output(output))
    if method == "password":
        wrapped = " ".join(shlex.quote(part) for part in wrap_remote_login_shell(remote_cmd))
        command = f"{shlex.quote(str(SSH_PASSWORD_EXEC))} {shlex.quote(host)} {shlex.quote(port)} {shlex.quote(user)} -- {wrapped}"
        output = run_checked(["bash", "-lc", command], env=env)
        return "\n".join(clean_remote_output(output))
    raise RuntimeError(f"unsupported login method: {method}")


def remote_api_json(login: Dict[str, str], state: Dict[str, str], api_base_url: str, env: Dict[str, str]) -> dict:
    output = run_remote_simple(login, state, f"curl -sS {shlex.quote(api_base_url + '/api/tasks')}", env)
    lines = clean_remote_output(output)
    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise RuntimeError(f"failed to parse remote api json: {output}")


def gather_remote_files(login: Dict[str, str], state: Dict[str, str], app_dir: str, logging_dir: str, env: Dict[str, str]) -> dict:
    marker = "__SDSKILL_JSON__"
    remote_cmd = (
        f"export APP_DIR={shlex.quote(app_dir)} LOG_DIR={shlex.quote(logging_dir)}; "
        "if command -v python >/dev/null 2>&1; then PY=python; "
        "elif command -v python3 >/dev/null 2>&1; then PY=python3; "
        "else echo python-interpreter-not-found >&2; exit 127; fi; "
        "$PY - <<'PY'\n"
        "import json, os\n"
        "from pathlib import Path\n"
        "app_dir = Path(os.environ['APP_DIR'])\n"
        "log_dir = Path(os.environ['LOG_DIR'])\n"
        "logs = sorted((app_dir / 'logs').glob('lora-scripts-main-*.log'), key=lambda p: p.stat().st_mtime if p.exists() else 0)\n"
        "latest_log = logs[-1] if logs else None\n"
        "event_files = sorted(str(p) for p in log_dir.rglob('events.out.tfevents*')) if log_dir.exists() else []\n"
        "payload = {\n"
        "  'latest_log': str(latest_log) if latest_log else '',\n"
        "  'event_files': event_files,\n"
        "}\n"
        f"print('{marker}')\n"
        "print(json.dumps(payload, ensure_ascii=False))\n"
        "PY"
    )
    output = run_remote_simple(login, state, remote_cmd, env)
    lines = clean_remote_output(output)
    if marker not in lines:
        raise RuntimeError(f"failed to gather remote files: {output}")
    index = lines.index(marker)
    return json.loads(lines[index + 1])


def gather_remote_log_analysis(login: Dict[str, str], state: Dict[str, str], log_path: str, task_id: str, env: Dict[str, str]) -> dict:
    if not log_path:
        return {"segment_text": "", "progress_samples": []}
    marker = "__SDSKILL_JSON__"
    remote_cmd = (
        f"export LOG_PATH={shlex.quote(log_path)} TASK_ID={shlex.quote(task_id)}; "
        "if command -v python >/dev/null 2>&1; then PY=python; "
        "elif command -v python3 >/dev/null 2>&1; then PY=python3; "
        "else echo python-interpreter-not-found >&2; exit 127; fi; "
        "$PY - <<'PY'\n"
        "import json, os, re\n"
        "from pathlib import Path\n"
        "text = Path(os.environ['LOG_PATH']).read_text(encoding='utf-8', errors='ignore') if Path(os.environ['LOG_PATH']).exists() else ''\n"
        "task_id = os.environ.get('TASK_ID', '')\n"
        "task_index = text.rfind(f'Task {task_id} created') if task_id else -1\n"
        "start_markers = [text.rfind('Training started with config file')]\n"
        "start_index = max(start_markers)\n"
        "if task_index >= 0:\n"
        "    earlier = [index for index in start_markers if 0 <= index <= task_index]\n"
        "    start_index = max(earlier) if earlier else task_index\n"
        "segment = text[start_index:] if start_index >= 0 else text\n"
        "progress = re.findall(r'steps:\\s*(\\d+)/(\\d+).*?avr_loss=([0-9.]+)', segment)\n"
        "payload = {'segment_text': segment[-12000:], 'progress_samples': progress[-20:]}\n"
        f"print('{marker}')\n"
        "print(json.dumps(payload, ensure_ascii=False))\n"
        "PY"
    )
    output = run_remote_simple(login, state, remote_cmd, env)
    lines = clean_remote_output(output)
    if marker not in lines:
        return {"segment_text": output, "progress_samples": []}
    index = lines.index(marker)
    return json.loads(lines[index + 1])


def read_remote_log_tail(login: Dict[str, str], state: Dict[str, str], log_path: str, env: Dict[str, str], lines: int = 400) -> str:
    if not log_path:
        return ""
    remote_cmd = f"if [ -f {shlex.quote(log_path)} ]; then tail -n {lines} {shlex.quote(log_path)}; fi"
    return run_remote_simple(login, state, remote_cmd, env)


def maybe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "on"}:
            return True
        if text in {"false", "0", "no", "off"}:
            return False
    return None


def numeric_string_issue(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    return bool(NUMERIC_RE.fullmatch(text) or RANGE_RE.match(text))


def find_active_task(tasks_payload: dict, task_id: str) -> dict | None:
    tasks = (((tasks_payload.get("data") or {}).get("tasks")) or []) if isinstance(tasks_payload, dict) else []
    if task_id:
        for item in tasks:
            value = str(item.get("id") or item.get("task_id") or item.get("uuid") or "")
            if value == task_id:
                return item
    for item in reversed(tasks):
        status = str(item.get("status") or "")
        if status == "RUNNING":
            return item
    return tasks[-1] if tasks else None


def segment_current_run(log_text: str, task_id: str) -> str:
    stripped = sanitize(log_text)
    task_index = stripped.rfind(f"Task {task_id} created") if task_id else -1
    start_markers = [stripped.rfind("Training started with config file")]
    start_index = max(start_markers)
    if task_index >= 0:
        earlier_markers = [index for index in start_markers if 0 <= index <= task_index]
        if earlier_markers:
            start_index = max(earlier_markers)
        else:
            start_index = task_index
    if start_index < 0:
        return stripped
    return stripped[start_index:]


def parse_progress(log_text: str) -> dict:
    stripped = sanitize(log_text)
    matches = PROGRESS_RE.findall(stripped)
    if not matches:
        return {"current_step": "", "total_steps": "", "progress_percent": "", "latest_avr_loss": "", "loss_samples": []}
    samples = []
    for current, total, loss in matches[-20:]:
        try:
            current_i = int(current)
            total_i = int(total)
            loss_f = float(loss)
        except ValueError:
            continue
        samples.append((current_i, total_i, loss_f))
    if not samples:
        return {"current_step": "", "total_steps": "", "progress_percent": "", "latest_avr_loss": "", "loss_samples": []}
    current_step, total_steps, latest_loss = samples[-1]
    progress_percent = round(current_step * 100 / total_steps, 2) if total_steps else ""
    return {
        "current_step": current_step,
        "total_steps": total_steps,
        "progress_percent": progress_percent,
        "latest_avr_loss": latest_loss,
        "loss_samples": samples,
    }


def detect_confirmed_errors(log_text: str) -> List[dict]:
    stripped = sanitize(log_text)
    findings: List[dict] = []
    for pattern, severity, title, action in ERROR_PATTERNS:
        if pattern.search(stripped):
            findings.append({"severity": severity, "title": title, "detail": title, "action": action})
    return findings


def dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def render_list(items: List[dict], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}\n"
    lines = []
    for item in items:
        severity = item.get("severity", "info")
        title = sanitize_inline(str(item.get("title") or ""))
        detail = sanitize_inline(str(item.get("detail") or ""))
        text = title if not detail or detail == title else f"{title}：{detail}"
        lines.append(f"- [{severity}] {text}")
    return "\n".join(lines).rstrip() + "\n"


def append_timeline(base: Path, line: str) -> None:
    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as file:
        file.write(f"- {now_iso()} {line}\n")


def load_analysis_history(path: Path) -> List[str]:
    return load_history_lines(path, "## History\n")


def write_analysis_markdown(base: Path, summary: dict, confirmed: List[dict], inferred: List[dict], actions: List[str]) -> Path:
    path = base / "training" / "analysis.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    history = load_analysis_history(path)
    history.append(
        f"- {now_iso()} | run={summary['run_name']} | status={summary['overall_status']} | data={summary['data_status']} | runtime={summary['runtime_status']} | finding={sanitize_inline(summary['primary_finding'])}"
    )
    history_text = "\n".join(history).rstrip()
    if history_text:
        history_text += "\n"
    latest_loss = summary.get("latest_avr_loss", "")
    latest_loss_text = "" if latest_loss == "" else latest_loss
    text = (
        "# LoRA Training Analysis\n\n"
        "## Latest Analysis\n"
        f"- Run Name: {summary['run_name']}\n"
        f"- Scope: {summary['scope']}\n"
        f"- Overall Status: {summary['overall_status']}\n"
        f"- Data Status: {summary['data_status']}\n"
        f"- Runtime Status: {summary['runtime_status']}\n"
        f"- Current Step: {summary['current_step']}\n"
        f"- Total Steps: {summary['total_steps']}\n"
        f"- Progress Percent: {summary['progress_percent']}\n"
        f"- Latest Average Loss: {latest_loss_text}\n"
        f"- Validation Signal: {summary['validation_signal']}\n"
        f"- TensorBoard Event Count: {summary['event_count']}\n"
        f"- Primary Finding: {summary['primary_finding']}\n"
        f"- Suggested Action: {summary['suggested_action']}\n"
        f"- Notes: {summary['notes']}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Confirmed Findings\n"
        f"{render_list(confirmed, '未发现已确认的硬问题。')}\n"
        "## Inferred Risks\n"
        f"{render_list(inferred, '当前没有明显推断风险。')}\n"
        "## Suggested Actions\n"
        f"{'\n'.join(f'- {sanitize_inline(item)}' for item in actions) if actions else '- 暂无额外动作。'}\n\n"
        "## History\n"
        f"{history_text}"
    )
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze one LoRA training run from the current AutoDL workspace.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("--run-name", default="")
    parser.add_argument("--api-base-url", default="")
    parser.add_argument("--app-dir", default="/root/autodl-tmp/lora-scripts/app")
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    base = workspace_root / "servers" / args.server_alias
    state = parse_markdown_kv(base / "state.md")
    login = parse_markdown_kv(base / "login" / "method.md")
    service = parse_markdown_kv(base / "services" / "lora-scripts.md")
    train_state = parse_markdown_kv(base / "training" / "lora.md")
    dataset = parse_markdown_kv(base / "training" / "datasets.md")
    configs = parse_markdown_kv(base / "training" / "configs.md")

    run_name = args.run_name or train_state.get("Run Name", "") or "current-run"
    api_base_url = args.api_base_url or train_state.get("API Base URL", "") or service.get("Service URL", "") or "http://127.0.0.1:28000"
    prepared_path_value = configs.get("Prepared Path", "")
    prepared_path = resolve_rel(base, prepared_path_value) if prepared_path_value else None
    if (not prepared_path or not prepared_path.exists()) and (base / "training" / "prepared-configs").exists():
        candidates = sorted((base / "training" / "prepared-configs").glob("*.json"))
        prepared_path = candidates[-1] if candidates else None

    config: Dict[str, Any] = {}
    if prepared_path and prepared_path.exists():
        config = json.loads(prepared_path.read_text(encoding="utf-8"))

    confirmed: List[dict] = []
    inferred: List[dict] = []
    actions: List[str] = []
    notes: List[str] = []

    image_count = int(dataset.get("Image Count", "0") or 0)
    paired_count = int(dataset.get("Paired Count", "0") or 0)
    missing_caption_count = int(dataset.get("Missing Caption Count", "0") or 0)
    orphan_caption_count = int(dataset.get("Orphan Caption Count", "0") or 0)
    needs_resize_count = int(dataset.get("Needs Resize Count", "0") or 0)
    dataset_status = dataset.get("Status", "unknown") or "unknown"

    if missing_caption_count > 0:
        confirmed.append({"severity": "high", "title": "训练集缺少同名 caption", "detail": f"missing_caption_count={missing_caption_count}", "action": "先补齐缺失 caption，再继续训练。"})
        actions.append("先补齐缺失的同名 `.txt` 标注文件。")
    if orphan_caption_count > 0:
        confirmed.append({"severity": "medium", "title": "训练集存在孤立 caption", "detail": f"orphan_caption_count={orphan_caption_count}", "action": "清理多余 caption，避免误判数据规模。"})
        actions.append("清理没有对应图片的 `.txt` 文件。")
    if image_count and paired_count and paired_count < image_count:
        confirmed.append({"severity": "medium", "title": "已配对图片少于总图片数", "detail": f"paired={paired_count}/{image_count}", "action": "先把未配对图片补齐标注。"})
    if needs_resize_count > 0 and dataset_status not in {"prepared", "ready"}:
        confirmed.append({"severity": "medium", "title": "训练集仍有尺寸待处理图片", "detail": f"needs_resize_count={needs_resize_count}", "action": "先完成 64 倍数裁剪或补白。"})
        actions.append("先把非 64 倍数图片处理到可训练尺寸。")

    numeric_string_keys = []
    for key in sorted(NUMERIC_KEYS):
        if key in config and numeric_string_issue(config[key]):
            numeric_string_keys.append(key)
    if numeric_string_keys:
        confirmed.append({"severity": "high", "title": "训练配置仍有数值字符串", "detail": ", ".join(numeric_string_keys), "action": "先通过配置准备 skill 归一化数值，再重新启动。"})
        actions.append("先把配置里的学习率、epoch、batch 等字符串数值转成真正数值。")

    cache_text_encoder_outputs = maybe_bool(config.get("cache_text_encoder_outputs"))
    network_train_unet_only = maybe_bool(config.get("network_train_unet_only"))
    shuffle_caption = maybe_bool(config.get("shuffle_caption"))
    keep_tokens = config.get("keep_tokens", "")
    scenario = train_state.get("Scenario", "") or "other"
    validation_signal = "not-configured"
    if config.get("validation_prompt") or config.get("val_dataset_config"):
        validation_signal = "configured"
    else:
        inferred.append({"severity": "info", "title": "未配置验证样张或验证集（推断置信度较低）", "detail": "当前更适合把 loss 走势当成辅助信号，而不是最终质量结论。"})
        actions.append("若要更稳地判断过拟合，补上 validation_prompt 或 val_dataset_config。")

    if cache_text_encoder_outputs:
        if network_train_unet_only is False:
            confirmed.append({"severity": "high", "title": "cache_text_encoder_outputs 与当前训练目标冲突", "detail": "官方文档说明启用后 text encoder 不会被训练。", "action": "若要训练 text encoder，请关闭 cache_text_encoder_outputs；否则改成仅训 U-Net。"})
            actions.append("若你想训练 text encoder，请关闭 `cache_text_encoder_outputs`。")
        if shuffle_caption:
            confirmed.append({"severity": "medium", "title": "shuffle_caption 在当前配置下不会生效", "detail": "官方文档说明缓存 text encoder 输出后，caption shuffle/dropout 类增强会失效。", "action": "若你想保留 caption 增强，请关闭 cache_text_encoder_outputs。"})

    if shuffle_caption and scenario in {"character", "outfit-accessory"}:
        try:
            keep_tokens_value = int(keep_tokens)
        except Exception:
            keep_tokens_value = None
        if keep_tokens_value == 0:
            inferred.append({"severity": "medium", "title": "角色/服装场景的触发词稳定性可能偏弱（推断）", "detail": "当前启用了 shuffle_caption，但 keep_tokens=0，前部 token 不会被固定。"})
            actions.append("若角色触发词不稳，可把 `keep_tokens` 提到 1 或更高。")

    if maybe_bool(config.get("bucket_no_upscale")) and (config.get("min_bucket_reso") or config.get("max_bucket_reso")):
        inferred.append({"severity": "info", "title": "bucket_no_upscale 已开启（推断）", "detail": "官方文档说明此时 min/max bucket reso 会被忽略。"})

    runtime_status = "unknown"
    task_id = train_state.get("Task ID", "")
    event_count = 0
    current_step: Any = ""
    total_steps: Any = ""
    progress_percent: Any = ""
    latest_avr_loss: Any = ""
    primary_finding = "尚未完成训练诊断。"
    remote_ok = False

    if not args.local_only:
        env = os.environ.copy()
        try:
            logging_dir_value = str(config.get("logging_dir") or "./logs") if config else "./logs"
            if logging_dir_value.startswith("/"):
                logging_dir = logging_dir_value
            else:
                logging_dir = str((Path(args.app_dir) / logging_dir_value).resolve())
            tasks_payload = remote_api_json(login, state, api_base_url, env)
            active_task = find_active_task(tasks_payload, task_id)
            runtime_status = str((active_task or {}).get("status") or train_state.get("Status", "unknown") or "unknown")
            if active_task and not task_id:
                value = str(active_task.get("id") or active_task.get("task_id") or active_task.get("uuid") or "")
                if value:
                    task_id = value
            remote_files = gather_remote_files(login, state, args.app_dir, logging_dir, env)
            event_count = len(remote_files.get("event_files") or [])
            log_path = str(remote_files.get("latest_log") or "")
            log_tail = read_remote_log_tail(login, state, log_path, env)
            remote_log_analysis = gather_remote_log_analysis(login, state, log_path, task_id, env)
            current_segment = str(remote_log_analysis.get('segment_text') or segment_current_run(log_tail, task_id))
            progress = parse_progress(current_segment)
            if not progress.get('current_step'):
                samples = []
                for current, total, loss in remote_log_analysis.get('progress_samples') or []:
                    try:
                        samples.append((int(current), int(total), float(loss)))
                    except ValueError:
                        continue
                if samples:
                    current_step_value, total_steps_value, latest_loss_value = samples[-1]
                    progress = {
                        'current_step': current_step_value,
                        'total_steps': total_steps_value,
                        'progress_percent': round(current_step_value * 100 / total_steps_value, 2) if total_steps_value else '',
                        'latest_avr_loss': latest_loss_value,
                        'loss_samples': samples,
                    }
            current_step = progress["current_step"]
            total_steps = progress["total_steps"]
            progress_percent = progress["progress_percent"]
            latest_avr_loss = progress["latest_avr_loss"]
            confirmed.extend(detect_confirmed_errors(current_segment))
            remote_ok = True

            if runtime_status == "RUNNING" and event_count > 0 and current_step:
                primary_finding = f"训练已真实运行，当前约 {progress_percent}%（{current_step}/{total_steps}）。"
            elif runtime_status == "RUNNING" and event_count > 0:
                primary_finding = "训练已经启动，TensorBoard 事件文件已出现。"
            elif runtime_status == "RUNNING":
                confirmed.append({"severity": "medium", "title": "任务仍在 RUNNING，但还没有新的 TensorBoard event", "detail": "当前更像启动中的中间态。", "action": "继续监控到 event 文件出现。"})
                primary_finding = "任务仍在启动链路中，还不能算完全进入稳定训练。"
                actions.append("继续监控，直到 TensorBoard event 文件出现。")
            elif runtime_status == "FINISHED":
                if "Training finished" in current_segment or "训练完成" in current_segment or "model saved." in current_segment:
                    primary_finding = "训练已正常完成，并已保存最终模型文件。"
                else:
                    confirmed.append({"severity": "medium", "title": "任务已经结束", "detail": "需要结合日志判断是正常完成还是过早结束。", "action": "查看结束前最后一段日志和输出文件。"})
                    primary_finding = "任务已经结束，需要结合日志判断是否正常收尾。"
            elif runtime_status == "FAILED":
                primary_finding = "任务已经失败，应优先处理最后一个明确报错。"
            else:
                primary_finding = f"当前任务状态为 {runtime_status or 'unknown'}。"

            loss_samples = progress.get("loss_samples") or []
            if len(loss_samples) >= 8:
                first_loss = loss_samples[0][2]
                last_loss = loss_samples[-1][2]
                if last_loss > first_loss * 1.25:
                    inferred.append({"severity": "medium", "title": "最近 loss 有回升迹象（推断）", "detail": f"recent {first_loss:.4f} -> {last_loss:.4f}", "action": "结合样张与验证信号判断是否该降学习率或减弱训练强度。"})
                elif last_loss < first_loss * 0.85:
                    inferred.append({"severity": "info", "title": "最近 loss 仍在下降（推断）", "detail": f"recent {first_loss:.4f} -> {last_loss:.4f}"})
        except Exception as exc:
            error_line = sanitize_inline((str(exc).splitlines() or [str(exc)])[-1])[:240]
            notes.append(f"remote-check-degraded: {error_line}")
            runtime_status = train_state.get("Status", "unknown") or "unknown"
            inferred.append({"severity": "info", "title": "本次只完成了本地台账分析（推断）", "detail": "远端日志或 API 未完成补充检查。"})
            actions.append("若要拿到完整运行诊断，请带着当前 SSH 登录方式再跑一次分析。")

    if not remote_ok and not confirmed:
        primary_finding = "当前先完成了数据和配置层分析，运行时信号还不完整。"

    high_count = sum(1 for item in confirmed if item.get("severity") == "high")
    medium_count = sum(1 for item in confirmed if item.get("severity") == "medium")
    normal_finished = runtime_status == "FINISHED" and primary_finding == "训练已正常完成，并已保存最终模型文件。"
    if high_count:
        overall_status = "blocked"
    elif medium_count or runtime_status == "unknown":
        overall_status = "needs-attention"
    elif normal_finished:
        overall_status = "healthy"
    else:
        overall_status = "healthy"

    if missing_caption_count > 0 or needs_resize_count > 0:
        data_status = "needs-fix"
    elif dataset_status in {"prepared", "ready"} and image_count > 0:
        data_status = "ok"
    else:
        data_status = dataset_status

    if not actions:
        if overall_status == "healthy":
            actions.append("继续训练，并定期看 TensorBoard 标量与样张。")
        else:
            actions.append("先处理第一条已确认问题，再继续观察训练。")
    actions = dedupe_keep_order(actions)

    if high_count and confirmed:
        suggested_action = confirmed[0].get("action") or actions[0]
    else:
        suggested_action = actions[0]

    summary = {
        "run_name": run_name,
        "scope": "dataset+config+runtime" if remote_ok else "dataset+config",
        "overall_status": overall_status,
        "data_status": data_status,
        "runtime_status": runtime_status,
        "current_step": current_step,
        "total_steps": total_steps,
        "progress_percent": progress_percent,
        "latest_avr_loss": latest_avr_loss,
        "validation_signal": validation_signal,
        "event_count": event_count,
        "primary_finding": primary_finding,
        "suggested_action": suggested_action,
        "notes": "; ".join(notes) if notes else "",
        "task_id": task_id,
        "prepared_config": str(prepared_path) if prepared_path else "",
    }

    report_path = write_analysis_markdown(base, summary, confirmed, inferred, actions)
    append_timeline(base, f"updated LoRA analysis report (run={run_name}, status={overall_status}).")

    payload = {
        "summary": summary,
        "confirmed": confirmed,
        "inferred": inferred,
        "actions": actions,
        "report_path": str(report_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
