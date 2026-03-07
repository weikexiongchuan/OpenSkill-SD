#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_if_missing(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize local markdown workspace for one server.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    args = parser.parse_args()

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    (base / "login").mkdir(parents=True, exist_ok=True)
    (base / "services").mkdir(parents=True, exist_ok=True)
    (base / "training").mkdir(parents=True, exist_ok=True)
    (base / "storage").mkdir(parents=True, exist_ok=True)
    (base / "training" / "imported-configs").mkdir(parents=True, exist_ok=True)
    (base / "training" / "prepared-configs").mkdir(parents=True, exist_ok=True)
    (base / "training" / "sample-prompts").mkdir(parents=True, exist_ok=True)

    write_if_missing(
        base / "state.md",
        (
            f"# Server State: {args.server_alias}\n\n"
            "## Connection\n"
            "- Host: unknown\n"
            "- Port: unknown\n"
            "- User: unknown\n\n"
            "## Login Mode\n"
            "- Method: unknown\n"
            "- Identity File: \n"
            "- SSH Alias: \n\n"
            "## Runtime\n"
            "- Workspace Root: \n"
            f"- Last Verified: {now_iso()}\n"
            "- Status: unknown\n"
        ),
    )
    write_if_missing(
        base / "login" / "method.md",
        (
            "# Login Method\n\n"
            "- Method: unknown\n"
            "- Password Stored: no\n"
            "- Identity File: \n"
            "- SSH Alias: \n"
            f"- Updated At: {now_iso()}\n"
        ),
    )
    write_if_missing(
        base / "services" / "comfyui.md",
        (
            "# ComfyUI Service\n\n"
            "- Session: \n"
            "- Internal Port: \n"
            "- Access Mode: \n"
            "- Service URL: \n"
            "- Health: unknown\n"
            f"- Updated At: {now_iso()}\n"
        ),
    )
    write_if_missing(
        base / "services" / "lora-scripts.md",
        (
            "# LoRA Scripts Service\n\n"
            "- Session: \n"
            "- Service Port: \n"
            "- Tensorboard Port: \n"
            "- Access Mode: \n"
            "- Service URL: \n"
            "- Health: unknown\n"
            f"- Updated At: {now_iso()}\n"
        ),
    )
    write_if_missing(
        base / "training" / "lora.md",
        (
            "# LoRA Training State\n\n"
            "## Active Run\n"
            "- Run Name: \n"
            "- Template ID: \n"
            "- Scenario: \n"
            "- Model Train Type: \n"
            "- Status: unknown\n"
            "- Task ID: \n"
            "- API Base URL: \n"
            "- Output Name: \n"
            "- Output Dir: \n"
            "- Resume Checkpoint: \n"
            "- Notes: \n"
            f"- Updated At: {now_iso()}\n\n"
            "## Registered Runs\n"
        ),
    )
    write_if_missing(
        base / "training" / "models.md",
        (
            "# LoRA Base Model Registry\n\n"
            "## Latest Model\n"
            "- Slot ID: \n"
            "- Label: \n"
            "- Family: \n"
            "- Family Version: \n"
            "- Family Branch: \n"
            "- Repo ID: \n"
            "- Filename: \n"
            "- Download Mode: \n"
            "- Storage Tier: \n"
            "- Stored Path: \n"
            "- Active Path: \n"
            "- Status: unknown\n"
            "- Notes: \n"
            f"- Updated At: {now_iso()}\n\n"
            "## Registered Models\n"
        ),
    )
    write_if_missing(
        base / "training" / "datasets.md",
        (
            "# LoRA Training Dataset Registry\n\n"
            "## Latest Dataset\n"
            "- Dataset ID: \n"
            "- Label: \n"
            "- Source: \n"
            "- Storage Tier: \n"
            "- Stored Path: \n"
            "- Runtime Path: \n"
            "- Status: unknown\n"
            "- Size Policy: \n"
            "- Image Count: \n"
            "- Caption Count: \n"
            "- Paired Count: \n"
            "- Missing Caption Count: \n"
            "- Orphan Caption Count: \n"
            "- Duplicate Image Key Count: \n"
            "- Duplicate Caption Key Count: \n"
            "- Multiple Of 64 OK Count: \n"
            "- Needs Resize Count: \n"
            "- Resized Count: \n"
            "- Resize Error Count: \n"
            "- Notes: \n"
            f"- Updated At: {now_iso()}\n\n"
            "## Registered Datasets\n"
        ),
    )
    write_if_missing(
        base / "storage" / "large-files.md",
        (
            "# Large File Registry\n\n"
            "## Current Files\n\n"
            "## History\n"
        ),
    )
    write_if_missing(
        base / "training" / "sample-prompts.md",
        (
            "# LoRA Sample Prompt Registry\n\n"
            "## Latest Prompt Set\n"
            "- Prompt Set Name: \n"
            "- Source: \n"
            "- Prompt Count: \n"
            "- Dataset Dir: \n"
            "- File Path: \n"
            "- Sample Width: \n"
            "- Sample Height: \n"
            "- Sample CFG: \n"
            "- Sample Steps: \n"
            "- Sample Seed Base: \n"
            "- Sample Sampler: \n"
            "- Notes: \n"
            f"- Updated At: {now_iso()}\n\n"
            "## Prompt Preview\n"
            "## History\n"
        ),
    )
    write_if_missing(
        base / "training" / "analysis.md",
        (
            "# LoRA Training Analysis\n\n"
            "## Latest Analysis\n"
            "- Run Name: \n"
            "- Scope: \n"
            "- Overall Status: unknown\n"
            "- Data Status: unknown\n"
            "- Runtime Status: unknown\n"
            "- Current Step: \n"
            "- Total Steps: \n"
            "- Progress Percent: \n"
            "- Latest Average Loss: \n"
            "- Validation Signal: unknown\n"
            "- TensorBoard Event Count: \n"
            "- Primary Finding: \n"
            "- Suggested Action: \n"
            "- Notes: \n"
            f"- Updated At: {now_iso()}\n\n"
            "## Confirmed Findings\n"
            "## Inferred Risks\n"
            "## Suggested Actions\n"
            "## History\n"
        ),
    )
    write_if_missing(
        base / "training" / "configs.md",
        (
            "# LoRA Training Config Registry\n\n"
            "## Latest Config\n"
            "- Config Name: \n"
            "- Source: \n"
            "- Stage: \n"
            "- File Type: \n"
            "- Parse Status: \n"
            "- Original Path: \n"
            "- Stored Path: \n"
            "- Prepared Path: \n"
            "- Selected Preset: \n"
            "- Model Train Type: \n"
            "- Base Model Path: \n"
            "- Train Data Dir: \n"
            "- Output Name: \n"
            "- Notes: \n"
            f"- Updated At: {now_iso()}\n\n"
            "## Registered Configs\n"
        ),
    )
    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text(
            "# Timeline\n\n"
            f"- {now_iso()} initialized server state workspace.\n",
            encoding="utf-8",
        )

    print(f"initialized local workspace: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
