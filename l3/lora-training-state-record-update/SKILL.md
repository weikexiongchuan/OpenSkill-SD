---
name: lora-training-state-record-update
description: Atomic capability skill for updating `training/lora.md` and related timeline entries inside the canonical local server workspace. Use for dynamically registering lora-scripts training runs to the corresponding server after template selection, task start, task status refresh, finish, failure, or termination.
---

# LoRA Training State Record Update

## Purpose
Update local per-server LoRA training markdown records.

## Capabilities
- Write the active training section in `training/lora.md`.
- Append or refresh one registered training-run entry.
- Register the output directory in `storage/large-files.md` when it is known.
- Append matching `timeline.md` entries.
- Keep template choice, scenario, task id, status, and output path tied to the correct server workspace.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- run name and optional task id
- template id and scenario name
- model train type and status
- optional API base URL, output name, output directory, resume checkpoint, notes

## Typical Outputs
- Updated `training/lora.md`
- Updated `storage/large-files.md` when output dir is provided
- Appended `timeline.md` entry

## Route
- Use this skill whenever a lora-scripts training run is created, refreshed, finished, failed, or terminated.
- Use `l3/local-server-state-workspace-init` first if the workspace skeleton does not exist yet.
- Use this after `l3/lora-scripts-api-training-task` whenever API task state changes.

## Load On Demand
- `scripts/record_lora_training_state.py`
