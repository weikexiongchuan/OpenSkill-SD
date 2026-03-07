#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs(base: Path) -> None:
    (base / "training").mkdir(parents=True, exist_ok=True)
    (base / "storage").mkdir(parents=True, exist_ok=True)


def append_timeline(base: Path, line: str) -> None:
    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as file:
        file.write(f"- {now_iso()} {line}\n")


def load_history(path: Path, marker: str) -> List[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    if marker not in content:
        return []
    block = content.split(marker, 1)[1]
    return [line for line in block.splitlines() if line.startswith("- ")]


def load_current_large_files(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    start_marker = "## Current Files\n"
    end_marker = "\n## History\n"
    if start_marker not in content or end_marker not in content:
        return {}
    current_block = content.split(start_marker, 1)[1].split(end_marker, 1)[0]
    entries: Dict[str, str] = {}
    for line in current_block.splitlines():
        line = line.strip()
        if not line.startswith("- id="):
            continue
        asset_id = line.split(" | ", 1)[0].replace("- id=", "", 1).strip()
        entries[asset_id] = line
    return entries


def render_large_file_registry(entries: Dict[str, str], history: List[str]) -> str:
    current_lines = [entries[key] for key in sorted(entries)]
    current_text = "\n".join(current_lines).rstrip()
    if current_text:
        current_text += "\n"
    history_text = "\n".join(history).rstrip()
    if history_text:
        history_text += "\n"
    return (
        "# Large File Registry\n\n"
        "## Current Files\n"
        f"{current_text}\n"
        "## History\n"
        f"{history_text}"
    )


def sanitize_notes(value: str) -> str:
    return (value or "").replace("|", "/").replace("\n", " ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Record LoRA dataset state in local markdown workspace.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("dataset_id")
    parser.add_argument("label")
    parser.add_argument("source")
    parser.add_argument("storage_tier")
    parser.add_argument("stored_path")
    parser.add_argument("runtime_path")
    parser.add_argument("status")
    parser.add_argument("size_policy")
    parser.add_argument("summary_json")
    parser.add_argument("notes", nargs="?", default="")
    args = parser.parse_args()

    summary = json.loads(args.summary_json)
    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    ensure_dirs(base)

    datasets_file = base / "training" / "datasets.md"
    history = load_history(datasets_file, "## Registered Datasets\n")
    history.append(
        f"- {now_iso()} | id={args.dataset_id} | status={args.status} | source={args.source} | "
        f"images={summary.get('image_count', 0)} | paired={summary.get('paired_count', 0)} | "
        f"missing={summary.get('missing_caption_count', 0)} | orphan={summary.get('orphan_caption_count', 0)} | "
        f"resized={summary.get('resized_count', 0)} | size={args.size_policy} | path={args.runtime_path}"
    )
    history_text = "\n".join(history).rstrip()
    if history_text:
        history_text += "\n"

    notes = sanitize_notes(args.notes)
    datasets_text = (
        "# LoRA Training Dataset Registry\n\n"
        "## Latest Dataset\n"
        f"- Dataset ID: {args.dataset_id}\n"
        f"- Label: {args.label}\n"
        f"- Source: {args.source}\n"
        f"- Storage Tier: {args.storage_tier}\n"
        f"- Stored Path: {args.stored_path}\n"
        f"- Runtime Path: {args.runtime_path}\n"
        f"- Status: {args.status}\n"
        f"- Size Policy: {args.size_policy}\n"
        f"- Image Count: {summary.get('image_count', 0)}\n"
        f"- Caption Count: {summary.get('caption_count', 0)}\n"
        f"- Paired Count: {summary.get('paired_count', 0)}\n"
        f"- Missing Caption Count: {summary.get('missing_caption_count', 0)}\n"
        f"- Orphan Caption Count: {summary.get('orphan_caption_count', 0)}\n"
        f"- Duplicate Image Key Count: {summary.get('duplicate_image_key_count', 0)}\n"
        f"- Duplicate Caption Key Count: {summary.get('duplicate_caption_key_count', 0)}\n"
        f"- Multiple Of 64 OK Count: {summary.get('multiple_of_64_ok_count', 0)}\n"
        f"- Needs Resize Count: {summary.get('needs_resize_count', 0)}\n"
        f"- Resized Count: {summary.get('resized_count', 0)}\n"
        f"- Resize Error Count: {summary.get('resize_error_count', 0)}\n"
        f"- Notes: {notes}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Registered Datasets\n"
        f"{history_text}"
    )
    datasets_file.write_text(datasets_text, encoding="utf-8")

    large_file_registry = base / "storage" / "large-files.md"
    current_entries = load_current_large_files(large_file_registry)
    large_notes = sanitize_notes(
        f"paired={summary.get('paired_count', 0)}/{summary.get('image_count', 0)}; "
        f"resized={summary.get('resized_count', 0)}; {notes}"
    )
    current_entries[args.dataset_id] = (
        f"- id={args.dataset_id} | kind=dataset | label={args.label} | tier={args.storage_tier} | "
        f"status={args.status} | source={args.source} | stored={args.stored_path} | runtime={args.runtime_path} | notes={large_notes}"
    )
    large_history = load_history(large_file_registry, "## History\n")
    large_history.append(
        f"- {now_iso()} | id={args.dataset_id} | kind=dataset | tier={args.storage_tier} | "
        f"status={args.status} | source={args.source} | stored={args.stored_path}"
    )
    large_file_registry.write_text(render_large_file_registry(current_entries, large_history), encoding="utf-8")

    append_timeline(base, f"updated LoRA dataset record (id={args.dataset_id}, status={args.status}).")
    print(f"updated dataset markdown: {datasets_file}")
    print(f"updated large-file registry: {large_file_registry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
