#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Record LoRA basemodel state in local markdown workspace.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("slot_id")
    parser.add_argument("label")
    parser.add_argument("family")
    parser.add_argument("family_version")
    parser.add_argument("family_branch")
    parser.add_argument("repo_id")
    parser.add_argument("filename")
    parser.add_argument("download_mode")
    parser.add_argument("storage_tier")
    parser.add_argument("stored_path")
    parser.add_argument("active_path")
    parser.add_argument("status", choices=["planned", "downloaded", "linked", "failed", "manual-upload", "unknown"])
    parser.add_argument("notes", nargs="?", default="")
    args = parser.parse_args()

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    ensure_dirs(base)

    models_file = base / "training" / "models.md"
    model_history = load_history(models_file, "## Registered Models\n")
    model_history.append(
        f"- {now_iso()} | slot={args.slot_id} | family={args.family} | version={args.family_version} | "
        f"branch={args.family_branch} | status={args.status} | mode={args.download_mode} | file={args.filename} | path={args.stored_path}"
    )
    models_text = (
        "# LoRA Base Model Registry\n\n"
        "## Latest Model\n"
        f"- Slot ID: {args.slot_id}\n"
        f"- Label: {args.label}\n"
        f"- Family: {args.family}\n"
        f"- Family Version: {args.family_version}\n"
        f"- Family Branch: {args.family_branch}\n"
        f"- Repo ID: {args.repo_id}\n"
        f"- Filename: {args.filename}\n"
        f"- Download Mode: {args.download_mode}\n"
        f"- Storage Tier: {args.storage_tier}\n"
        f"- Stored Path: {args.stored_path}\n"
        f"- Active Path: {args.active_path}\n"
        f"- Status: {args.status}\n"
        f"- Notes: {args.notes}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Registered Models\n"
        + "\n".join(model_history).rstrip()
        + "\n"
    )
    models_file.write_text(models_text, encoding="utf-8")

    large_file_registry = base / "storage" / "large-files.md"
    current_entries = load_current_large_files(large_file_registry)
    current_entries[args.slot_id] = (
        f"- id={args.slot_id} | kind=basemodel | label={args.label} | tier={args.storage_tier} | "
        f"status={args.status} | source={args.download_mode} | stored={args.stored_path} | runtime={args.active_path} | notes={args.notes}"
    )
    large_history = load_history(large_file_registry, "## History\n")
    large_history.append(
        f"- {now_iso()} | id={args.slot_id} | kind=basemodel | tier={args.storage_tier} | "
        f"status={args.status} | source={args.download_mode} | stored={args.stored_path}"
    )
    large_file_registry.write_text(render_large_file_registry(current_entries, large_history), encoding="utf-8")

    append_timeline(base, f"updated LoRA base model record (slot={args.slot_id}, status={args.status}).")
    print(f"updated base model markdown: {models_file}")
    print(f"updated large-file registry: {large_file_registry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
