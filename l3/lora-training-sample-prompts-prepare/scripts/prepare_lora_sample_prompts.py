#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[3]
SSH_PASSWORD_EXEC = ROOT / "l3" / "ssh-server-connect" / "scripts" / "ssh_password_exec.sh"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._") or "sample-prompts"


def parse_markdown_kv(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            data[key.strip()] = value.strip()
    return data


def load_history(path: Path, marker: str) -> List[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    if marker not in content:
        return []
    block = content.split(marker, 1)[1]
    return [line for line in block.splitlines() if line.startswith("- ")]


def append_timeline(base: Path, line: str) -> None:
    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as file:
        file.write(f"- {now_iso()} {line}\n")


def clean_remote_output(text: str) -> List[str]:
    lines = []
    for raw in (text or "").splitlines():
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
    raise RuntimeError(f"unsupported login method: {method}")


def read_remote_captions(login: Dict[str, str], state: Dict[str, str], dataset_dir: str, env: Dict[str, str]) -> List[str]:
    marker = "__SDSKILL_JSON__"
    remote_cmd = (
        f"export DATASET_DIR={shlex.quote(dataset_dir)}; "
        "if command -v python >/dev/null 2>&1; then PY=python; "
        "elif command -v python3 >/dev/null 2>&1; then PY=python3; "
        "else echo python-interpreter-not-found >&2; exit 127; fi; "
        "$PY - <<'PY'\n"
        "import json, os\n"
        "from pathlib import Path\n"
        "dataset_dir = Path(os.environ['DATASET_DIR'])\n"
        "caps = []\n"
        "if dataset_dir.exists():\n"
        "    for path in sorted(dataset_dir.rglob('*.txt')):\n"
        "        try:\n"
        "            text = path.read_text(encoding='utf-8', errors='ignore').strip()\n"
        "        except Exception:\n"
        "            continue\n"
        "        if text:\n"
        "            caps.append({'path': str(path), 'text': text})\n"
        f"print('{marker}')\n"
        "print(json.dumps(caps, ensure_ascii=False))\n"
        "PY"
    )
    output = run_remote_simple(login, state, remote_cmd, env)
    lines = clean_remote_output(output)
    if marker not in lines:
        raise RuntimeError(f"failed to read remote captions: {output}")
    index = lines.index(marker)
    return json.loads(lines[index + 1])


def looks_like_prompt_line(text: str) -> bool:
    return any(flag in text for flag in [" --n ", " --w ", " --h ", " --l ", " --s ", " --d "])


def build_prompt_line(prompt: str, negative: str, width: int, height: int, cfg: float, steps: int, seed: int) -> str:
    line = prompt.strip()
    if not line:
        return ""
    if looks_like_prompt_line(line):
        return line
    return f"{line} --n {negative} --w {width} --h {height} --l {cfg:g} --s {steps} --d {seed}"


def write_registry(base: Path, set_name: str, source: str, prompt_file: Path, dataset_dir: str, count: int, width: int, height: int, cfg: float, steps: int, seed_base: int, sampler: str, prompts: List[str], notes: str) -> Path:
    registry = base / "training" / "sample-prompts.md"
    history = load_history(registry, "## History\n")
    rel_file = prompt_file.relative_to(base).as_posix()
    history.append(f"- {now_iso()} | name={set_name} | source={source} | count={count} | sampler={sampler} | file={rel_file}")
    history_text = "\n".join(history).rstrip()
    if history_text:
        history_text += "\n"
    preview_lines = "\n".join(f"- {idx+1}: {prompt[:180]}" for idx, prompt in enumerate(prompts[:3]))
    if preview_lines:
        preview_lines += "\n"
    text = (
        "# LoRA Sample Prompt Registry\n\n"
        "## Latest Prompt Set\n"
        f"- Prompt Set Name: {set_name}\n"
        f"- Source: {source}\n"
        f"- Prompt Count: {count}\n"
        f"- Dataset Dir: {dataset_dir}\n"
        f"- File Path: {rel_file}\n"
        f"- Sample Width: {width}\n"
        f"- Sample Height: {height}\n"
        f"- Sample CFG: {cfg:g}\n"
        f"- Sample Steps: {steps}\n"
        f"- Sample Seed Base: {seed_base}\n"
        f"- Sample Sampler: {sampler}\n"
        f"- Notes: {notes}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Prompt Preview\n"
        f"{preview_lines}\n"
        "## History\n"
        f"{history_text}"
    )
    registry.write_text(text, encoding="utf-8")
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare sample-image prompts for LoRA training.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("mode", choices=["random-captions", "manual"])
    parser.add_argument("set_name", nargs="?", default="sample-prompts")
    parser.add_argument("notes", nargs="?", default="")
    parser.add_argument("--dataset-dir", default="")
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--prompt", action="append", default=[])
    parser.add_argument("--manual-prompts-file", default="")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--seed-base", type=int, default=1337)
    parser.add_argument("--sampler", default="euler_a")
    parser.add_argument("--negative-prompt", default="")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).expanduser().resolve()
    base = workspace_root / "servers" / args.server_alias
    (base / "training" / "sample-prompts").mkdir(parents=True, exist_ok=True)

    state = parse_markdown_kv(base / "state.md")
    login = parse_markdown_kv(base / "login" / "method.md")
    dataset = parse_markdown_kv(base / "training" / "datasets.md")
    dataset_dir = args.dataset_dir or dataset.get("Runtime Path", "") or dataset.get("Stored Path", "")
    if not dataset_dir and args.mode == "random-captions":
        raise SystemExit("dataset dir is required for random-captions mode")

    raw_prompts: List[str] = []
    env = os.environ.copy()
    if args.mode == "random-captions":
        captions = read_remote_captions(login, state, dataset_dir, env)
        texts = [item.get("text", "").strip() for item in captions if item.get("text", "").strip()]
        if not texts:
            raise SystemExit("no caption txt found in remote dataset")
        count = max(1, min(args.count, len(texts)))
        raw_prompts = random.sample(texts, count)
    else:
        raw_prompts.extend([item.strip() for item in args.prompt if item.strip()])
        if args.manual_prompts_file:
            manual_file = Path(args.manual_prompts_file).expanduser().resolve()
            raw_prompts.extend([line.strip() for line in manual_file.read_text(encoding="utf-8").splitlines() if line.strip()])
        if not raw_prompts:
            raise SystemExit("manual mode requires at least one prompt")
        count = len(raw_prompts)

    final_lines = []
    for index, prompt in enumerate(raw_prompts):
        seed = args.seed_base + index
        line = build_prompt_line(prompt, args.negative_prompt, args.width, args.height, args.cfg, args.steps, seed)
        if line:
            final_lines.append(line)

    if not final_lines:
        raise SystemExit("no usable sample prompts generated")

    stored_name = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}__sample-prompts__{slugify(args.set_name)}.txt"
    stored_path = base / "training" / "sample-prompts" / stored_name
    stored_path.write_text("\n".join(final_lines) + "\n", encoding="utf-8")

    registry = write_registry(
        base,
        set_name=args.set_name,
        source=args.mode,
        prompt_file=stored_path,
        dataset_dir=dataset_dir,
        count=len(final_lines),
        width=args.width,
        height=args.height,
        cfg=args.cfg,
        steps=args.steps,
        seed_base=args.seed_base,
        sampler=args.sampler,
        prompts=final_lines,
        notes=args.notes,
    )
    append_timeline(base, f"prepared LoRA sample prompts (name={args.set_name}, source={args.mode}, count={len(final_lines)}).")

    print(json.dumps({
        "prompt_file": str(stored_path),
        "prompt_count": len(final_lines),
        "source": args.mode,
        "sampler": args.sampler,
        "registry": str(registry),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
