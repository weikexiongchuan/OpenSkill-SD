#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

CATALOG = {
    "noobai": {
        "display_name": "NoobAI XL",
        "require_branch": True,
        "default_slot": "noobai-xl-1.1-epsilon",
        "slots": {
            "noobai-xl-1.1-epsilon": {
                "label": "NoobAI XL 1.1",
                "version": "1.1",
                "branch": "epsilon",
                "repo_id": "Laxhar/noobai-XL-1.1",
                "filename": "NoobAI-XL-v1.1.safetensors",
                "persistent_subdir": "noobai-xl-1.1",
            },
            "noobai-xl-1.0-epsilon": {
                "label": "NoobAI XL 1.0",
                "version": "1.0",
                "branch": "epsilon",
                "repo_id": "Laxhar/noobai-XL-1.0",
                "filename": "NoobAI-XL-v1.0.safetensors",
                "persistent_subdir": "noobai-xl-1.0",
            },
            "noobai-xl-0.5-epsilon": {
                "label": "NoobAI XL 0.5",
                "version": "0.5",
                "branch": "epsilon",
                "repo_id": "Laxhar/noobai-XL-0.5",
                "filename": "NoobAI-XL-v0.5.safetensors",
                "persistent_subdir": "noobai-xl-0.5",
            },
            "noobai-xl-0.5-vpred": {
                "label": "NoobAI XL Vpred 0.5",
                "version": "0.5",
                "branch": "vpred",
                "repo_id": "Laxhar/noobai-XL-Vpred-0.5",
                "filename": "NoobAI-XL-VPred-v0.5.safetensors",
                "persistent_subdir": "noobai-xl-vpred-0.5",
            },
        },
    },
    "illustrious": {
        "display_name": "Illustrious XL",
        "require_branch": False,
        "default_slot": "illustrious-xl-1.1-standard",
        "slots": {
            "illustrious-xl-1.1-standard": {
                "label": "Illustrious XL 1.1",
                "version": "1.1",
                "branch": "standard",
                "repo_id": "OnomaAIResearch/Illustrious-XL-v1.1",
                "filename": "Illustrious-XL-v1.1.safetensors",
                "persistent_subdir": "illustrious-xl-1.1",
            },
            "illustrious-xl-1.0-standard": {
                "label": "Illustrious XL 1.0",
                "version": "1.0",
                "branch": "standard",
                "repo_id": "OnomaAIResearch/Illustrious-XL-v1.0",
                "filename": "Illustrious-XL-v1.0.safetensors",
                "persistent_subdir": "illustrious-xl-1.0",
            },
            "illustrious-xl-0.1-standard": {
                "label": "Illustrious XL 0.1",
                "version": "0.1",
                "branch": "standard",
                "repo_id": "OnomaAIResearch/Illustrious-xl-early-release-v0",
                "filename": "Illustrious-XL-v0.1.safetensors",
                "persistent_subdir": "illustrious-xl-0.1",
            },
            "illustrious-xl-0.1-guided": {
                "label": "Illustrious XL 0.1 Guided",
                "version": "0.1",
                "branch": "guided",
                "repo_id": "OnomaAIResearch/Illustrious-xl-early-release-v0",
                "filename": "Illustrious-XL-v0.1-GUIDED.safetensors",
                "persistent_subdir": "illustrious-xl-0.1-guided",
            },
        },
    },
}


def resolve_slot(family: str, version: str, branch: str, slot_id: str) -> tuple[str, dict]:
    family = family.strip().lower()
    if family not in CATALOG:
        raise SystemExit(f"unsupported family: {family}")
    family_data = CATALOG[family]
    if slot_id:
        slot = family_data["slots"].get(slot_id)
        if slot is None:
            raise SystemExit(f"unsupported slot_id for {family}: {slot_id}")
        return slot_id, slot
    if not version:
        slot_id = family_data["default_slot"]
        return slot_id, family_data["slots"][slot_id]
    branch_value = branch.strip().lower() or ("standard" if not family_data["require_branch"] else "")
    if family_data["require_branch"] and not branch_value:
        raise SystemExit(f"branch is required for family: {family}")
    for candidate_id, candidate in family_data["slots"].items():
        if candidate["version"] == version and candidate["branch"] == branch_value:
            return candidate_id, candidate
    raise SystemExit(f"unsupported version/branch for {family}: version={version}, branch={branch_value or '<empty>'}")


def build_command(repo_id: str, filename: str, persistent_dir: Path) -> str:
    lines = [
        "export HF_ENDPOINT=https://hf-mirror.com",
        f"mkdir -p {persistent_dir}",
        f"hf download {repo_id} {filename} --local-dir {persistent_dir}",
    ]
    return "\n".join(lines)


def build_activate_command(stored_path: Path, runtime_path: Path, activation_mode: str) -> str:
    if activation_mode == "none":
        return ""
    runtime_dir = runtime_path.parent
    if activation_mode == "copy":
        return f"mkdir -p {runtime_dir} && cp -f {stored_path} {runtime_path}"
    return f"mkdir -p {runtime_dir} && ln -sfn {stored_path} {runtime_path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve one LoRA basemodel slot into an AutoDL download plan.")
    parser.add_argument("family")
    parser.add_argument("version", nargs="?", default="")
    parser.add_argument("branch", nargs="?", default="")
    parser.add_argument("--slot-id", default="")
    parser.add_argument("--storage-root", default="/autodl-fs/data/models")
    parser.add_argument("--runtime-link-root", default="/root/autodl-tmp/lora-scripts/app/sd-models")
    parser.add_argument("--activation-mode", choices=["link", "copy", "none"], default="link")
    parser.add_argument("--filename-override", default="")
    args = parser.parse_args()

    slot_id, slot = resolve_slot(args.family, args.version, args.branch, args.slot_id)
    family = args.family.strip().lower()
    filename = args.filename_override.strip() or slot["filename"]
    persistent_dir = Path(args.storage_root).expanduser() / slot["persistent_subdir"]
    stored_path = persistent_dir / filename
    runtime_path = Path(args.runtime_link_root).expanduser() / filename

    payload = {
        "slot_id": slot_id,
        "family": family,
        "family_display_name": CATALOG[family]["display_name"],
        "label": slot["label"],
        "family_version": slot["version"],
        "family_branch": slot["branch"],
        "repo_id": slot["repo_id"],
        "filename": filename,
        "filename_source": "override" if args.filename_override.strip() else "catalog",
        "download_mode": "hf-mirror",
        "hf_endpoint": "https://hf-mirror.com",
        "persistent_dir": persistent_dir.as_posix(),
        "stored_path": stored_path.as_posix(),
        "runtime_path": runtime_path.as_posix(),
        "activation_mode": args.activation_mode,
        "download_command": build_command(slot["repo_id"], filename, persistent_dir),
        "activate_command": build_activate_command(stored_path, runtime_path, args.activation_mode),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
