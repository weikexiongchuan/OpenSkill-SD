#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def infer_storage_tier(path_value: str) -> str:
    value = (path_value or '').strip()
    if not value:
        return 'other'
    if value.startswith('/autodl-fs/') or value == '/autodl-fs':
        return 'fs'
    if value.startswith('/autodl-pub/') or value == '/autodl-pub':
        return 'pub'
    if value.startswith('/root/autodl-tmp/') or value == '/root/autodl-tmp':
        return 'tmp'
    return 'other'


def map_output_status(training_status: str) -> str:
    if training_status == 'failed':
        return 'failed'
    if training_status in {'queued', 'running', 'finished', 'terminated', 'template-selected'}:
        return 'linked'
    return 'unknown'


def update_large_file_registry(base: Path, output_id: str, run_name: str, output_dir: str, training_status: str) -> None:
    registry = base / 'storage' / 'large-files.md'
    registry.parent.mkdir(parents=True, exist_ok=True)
    if not registry.exists():
        registry.write_text('# Large File Registry\n\n## Current Files\n\n## History\n', encoding='utf-8')
    content = registry.read_text(encoding='utf-8')
    current_marker = '## Current Files\n'
    history_marker = '## History\n'
    if current_marker not in content or history_marker not in content:
        content = '# Large File Registry\n\n## Current Files\n\n## History\n'
    current_block = content.split(current_marker, 1)[1].split(history_marker, 1)[0]
    history_block = content.split(history_marker, 1)[1]
    current_lines = [line for line in current_block.splitlines() if line.startswith('- ')]
    history_lines = [line for line in history_block.splitlines() if line.startswith('- ')]

    tier = infer_storage_tier(output_dir)
    status = map_output_status(training_status)
    label = output_id or run_name
    notes = f'run={run_name};training-status={training_status}'
    current_line = (
        f'- id={output_id} | kind=output | label={label} | tier={tier} | status={status} | '
        f'source=generated | stored={output_dir} | runtime={output_dir} | notes={notes}'
    )
    current_lines = [line for line in current_lines if not (f'id={output_id} | kind=output |' in line)]
    current_lines.append(current_line)
    history_lines.append(
        f'- {now_iso()} | id={output_id} | kind=output | tier={tier} | status={status} | source=generated | stored={output_dir}'
    )

    current_text = '\n'.join(current_lines).rstrip()
    history_text = '\n'.join(history_lines).rstrip()
    if current_text:
        current_text += '\n'
    if history_text:
        history_text += '\n'
    registry.write_text(
        '# Large File Registry\n\n'
        '## Current Files\n'
        f'{current_text}\n'
        '## History\n'
        f'{history_text}',
        encoding='utf-8',
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs(base: Path) -> None:
    (base / "training").mkdir(parents=True, exist_ok=True)


def append_timeline(base: Path, line: str) -> None:
    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as file:
        file.write(f"- {now_iso()} {line}\n")


def load_history(training_file: Path) -> list[str]:
    if not training_file.exists():
        return []
    marker = "## Registered Runs\n"
    content = training_file.read_text(encoding="utf-8")
    if marker not in content:
        return []
    history_block = content.split(marker, 1)[1]
    return [line for line in history_block.splitlines() if line.startswith("- ")]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record LoRA training state in local markdown workspace.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("run_name")
    parser.add_argument("template_id")
    parser.add_argument("scenario", choices=["style", "character", "outfit-accessory", "other"])
    parser.add_argument("model_train_type")
    parser.add_argument(
        "status",
        choices=["template-selected", "queued", "running", "finished", "failed", "terminated", "unknown"],
    )
    parser.add_argument("task_id", nargs="?", default="")
    parser.add_argument("api_base_url", nargs="?", default="")
    parser.add_argument("output_name", nargs="?", default="")
    parser.add_argument("resume_checkpoint", nargs="?", default="")
    parser.add_argument("notes", nargs="?", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    ensure_dirs(base)

    training_file = base / "training" / "lora.md"
    history = load_history(training_file)
    history.append(
        f"- {now_iso()} | run={args.run_name} | template={args.template_id} | "
        f"scenario={args.scenario} | model={args.model_train_type} | status={args.status} | "
        f"task={args.task_id} | output={args.output_name} | output_dir={args.output_dir}"
    )
    history_text = "\n".join(history).rstrip() + "\n"

    text = (
        "# LoRA Training State\n\n"
        "## Active Run\n"
        f"- Run Name: {args.run_name}\n"
        f"- Template ID: {args.template_id}\n"
        f"- Scenario: {args.scenario}\n"
        f"- Model Train Type: {args.model_train_type}\n"
        f"- Status: {args.status}\n"
        f"- Task ID: {args.task_id}\n"
        f"- API Base URL: {args.api_base_url}\n"
        f"- Output Name: {args.output_name}\n"
        f"- Output Dir: {args.output_dir}\n"
        f"- Resume Checkpoint: {args.resume_checkpoint}\n"
        f"- Notes: {args.notes}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Registered Runs\n"
        f"{history_text}"
    )
    training_file.write_text(text, encoding="utf-8")

    if args.output_dir and (args.output_name or args.run_name):
        update_large_file_registry(base, args.output_name or args.run_name, args.run_name, args.output_dir, args.status)

    append_timeline(
        base,
        f"updated LoRA training state (run={args.run_name}, template={args.template_id}, status={args.status}).",
    )
    print(f"updated training markdown: {training_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
