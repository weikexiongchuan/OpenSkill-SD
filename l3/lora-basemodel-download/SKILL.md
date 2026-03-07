---
name: lora-basemodel-download
description: Atomic capability skill for resolving and recording supported LoRA base models for AutoDL training servers. Use when the user wants an exact base-model version slot, a ready remote-server download command through HF mirror, or a persistent record in the local server workspace.
---

# LoRA Basemodel Download

## Purpose
Resolve one supported base-model slot into an exact remote-server download plan and record it for the current server.

## Capabilities
- Resolve supported base-model slots into exact `repo_id`, filename, and target paths.
- Use `HF_ENDPOINT=https://hf-mirror.com` as the fixed mirror path for cataloged HuggingFace sources.
- Produce one persistent remote download path under `/autodl-fs/data/models/...`.
- Produce one optional runtime activation path under `/root/autodl-tmp/lora-scripts/app/sd-models/...`.
- Record planned or finished base-model state in `training/models.md`, `storage/large-files.md`, and append `timeline.md`.
- Run the remote-server download flow and report size / warmup ETA / periodic progress.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- family name such as `noobai` or `illustrious`
- explicit version and optional branch
- optional persistent storage root override
- optional runtime link root override
- optional activation mode override
- optional filename override when upstream file naming differs
- optional record status and notes

## Typical Outputs
- one exact model slot resolution
- one exact remote HF mirror download command
- one exact stored path and optional runtime path
- one monitored remote progress session with size, warmup ETA, and periodic updates
- updated `training/models.md` and `storage/large-files.md` when the record step is used

## Route
- Use this skill when the user chooses the download-script branch instead of manual upload.
- Use `l3/ssh-server-connect` when the exact remote command must be executed on the server.
- This skill is remote-server only; if remote download is too slow, fall back to local predownload plus upload into AutoDL 文件存储.
- If the user needs help for that fallback, provide download guidance and transfer/upload guidance.
- If the user has no VPN and the source file is hard to obtain, tell them they can contact the script author or the community for a usable source file.
- Do not encapsulate proxy parameters in this skill; keep proxy handling outside this skill.
- Use `l3/autodl-academic-model-download-acceleration` only when a separate remote download acceleration step is explicitly needed.
- Use `l3/local-server-state-workspace-init` first if the server workspace skeleton does not exist yet.

## Load On Demand
- `references/supported-basemodel-catalog.yaml`
- `references/download-and-record-playbook.md`
- `scripts/resolve_lora_basemodel_download.py`
- `scripts/record_lora_basemodel.py`
- `scripts/remote_hf_file_download.py`
- `scripts/run_remote_lora_basemodel_download.py`
