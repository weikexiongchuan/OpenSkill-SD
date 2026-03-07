---
name: lora-training-dataset-prepare
description: Atomic capability skill for getting one LoRA training dataset onto the current server and making it training-ready. Use for uploading a local dataset folder to the remote server, checking image/txt pairing, and fixing image sizes to 64 multiples with center crop by default or white padding on request.
---

# LoRA Training Dataset Prepare

## Purpose
Prepare one LoRA training dataset on the current server so it can be bound into a runnable training config.

## Capabilities
- Upload one local dataset directory to the current remote server over SSH.
- Reuse one existing remote dataset directory when the data is already on the server.
- Check whether each image has one same-name `.txt` caption file.
- Check whether image width and height are multiples of `64`.
- Fix image sizes on the server with center crop by default, or white padding when explicitly requested.
- Register dataset path and check result into `training/datasets.md`, `storage/large-files.md`, and `timeline.md`.

## Default Options
- Source path choice:
  - local dataset directory -> upload first `（推荐）`
  - existing remote dataset directory
- Remote storage choice:
  - `/autodl-fs/data/datasets` `（推荐）`
  - `/root/autodl-tmp/datasets`
- Size policy choice:
  - `crop`：向内居中裁剪到最接近的 `64` 倍数 `（推荐）`
  - `pad-white`：向上补白到最接近的 `64` 倍数
  - `check-only`：只检查，不改图
- 若用户在这些选项上只回复 `开始`、`直接开始`、`按默认` 或 `用推荐的`，就按 `local dataset directory + /autodl-fs/data/datasets + crop` 继续。

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- one dataset source path from local machine or remote server
- optional dataset name override
- optional remote destination path override
- optional size policy override
- optional output directory when the user wants a separate prepared copy instead of in-place fixing

## Typical Outputs
- one ready-to-train dataset directory on the remote server
- one dataset registry update in local workspace
- one large-file registry update in local workspace

## Route
- Use this skill after the user has chosen a training dataset, and before `l3/lora-training-config-prepare`.
- If the dataset is only on the user’s local computer, upload it to the current remote server first.
- If the dataset is already on the remote server or in AutoDL 文件存储, skip upload and run the dataset check directly on that remote path.
- If captions are missing, stop at the dataset report and let the user补齐数据；本 skill 不会自动生成标签。
- If only image sizes are off, fix them on the server with the selected size policy.
- Use `l3/local-server-state-workspace-init` first if the workspace skeleton does not exist yet.

## Load On Demand
- `scripts/run_remote_lora_dataset_prepare.py`
- `scripts/remote_prepare_lora_dataset.py`
- `scripts/record_lora_dataset.py`
