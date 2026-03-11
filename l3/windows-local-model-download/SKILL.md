---
name: windows-local-model-download
description: Atomic capability skill for resumable large-model downloads on a local Windows machine. Use when the user wants to download one checkpoint or base model locally, especially from HuggingFace mirror slots or a specific Civitai model version, and optionally hard-link it into ComfyUI or lora-scripts model directories.
---

# Windows Local Model Download

## Purpose
Download one large model file on a local Windows machine and optionally activate it for local apps.

## Capabilities
- Download one large file with resume support to a local persistent directory.
- Support cataloged HuggingFace base-model slots and direct Civitai model-version downloads.
- Verify actual byte growth instead of trusting a long-running process.
- Report file size, speed, and ETA from real disk progress.
- Hard-link one downloaded file into `ComfyUI` and `lora-scripts` model directories without duplicating storage.

## Typical Inputs
- one source type: `hf-slot`, `hf-url`, or `civitai-version`
- one exact file target path
- optional proxy URL
- optional local app targets such as `ComfyUI` or `lora-scripts`

## Typical Outputs
- one completed local model file
- one progress view based on actual bytes written
- optional hard links in local app directories

## Route
- Use this skill for exact “download this model locally on Windows” actions.
- Use `l3/lora-basemodel-download` first when the user still needs one exact NoobAI / Illustrious slot resolved from the workspace catalog.
- Use this skill directly when the source URL or Civitai version id is already known.
- Prefer resume-capable scripts over one-shot curl commands for multi-GB files.
- If the model should be visible to local apps after download, hard-link it into the target directories instead of copying the file again.

## Load On Demand
- `references/local-download-playbook.md`
- `references/source-patterns.md`
- `scripts/hf_resumable_download.py`
- `scripts/url_resumable_download.py`
- `scripts/link_local_model.py`

Load only the file that matches the next blocker:
- `references/local-download-playbook.md` for the core local workflow and progress policy.
- `references/source-patterns.md` when the user source is HuggingFace slot based or a Civitai version id.
- `scripts/hf_resumable_download.py` for HuggingFace mirror downloads with redirect resolution.
- `scripts/url_resumable_download.py` for direct URL downloads such as Civitai model endpoints.
- `scripts/link_local_model.py` when the downloaded file should be activated in local model directories.
