---
name: local-server-state-workspace-init
description: Atomic capability skill for initializing the local markdown workspace that stores per-server AutoDL state. Use for creating the folder skeleton and default `state.md`, `login/method.md`, `services/comfyui.md`, `services/lora-scripts.md`, `training/lora.md`, `training/models.md`, `training/datasets.md`, `training/configs.md`, and `timeline.md` files, including imported/prepared LoRA config storage.
---

# Local Server State Workspace Init

## Purpose
Create the local workspace skeleton defined by `l1/autodl-local-server-state-workspace`.

## Capabilities
- Create the canonical folder tree under `<workspace-root>/servers/<server-alias>/`.
- Create default markdown files with safe placeholder values.
- Prepare dataset registry, imported-config storage, prepared-config storage, and config registry files for later dataset prep, config import, and finalization.
- Prepare the workspace for later record updates.

## Typical Inputs
- `<workspace-root>`
- `<server-alias>`

## Typical Outputs
- Initialized local workspace tree
- Default markdown state files

## Route
- Use this before the first time a server is tracked locally.
- Read `l1/autodl-local-server-state-workspace` first if the schema is unclear.
