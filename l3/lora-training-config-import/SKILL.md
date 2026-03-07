---
name: lora-training-config-import
description: Atomic capability skill for importing a user-provided LoRA training config file into the canonical local server workspace. Use when the user already has a custom JSON or TOML config and wants it copied, registered, and clearly marked as `manual-import` under the corresponding server.
---

# LoRA Training Config Import

## Purpose
Import one user-provided training config into the local per-server workspace and register it for later use.

## Capabilities
- Copy one JSON or TOML config file into `training/imported-configs/` for the target server.
- Register the imported file in `training/configs.md`.
- Mark imported entries as `manual-import`.
- Append a matching `timeline.md` entry.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- one local config file path
- optional config name override
- optional note

## Typical Outputs
- copied config file under the target server workspace
- updated `training/configs.md`
- appended `timeline.md` entry

## Route
- Use this skill when the user already has a custom training config and wants it imported instead of starting from a built-in template.
- Use `l3/local-server-state-workspace-init` first if the workspace skeleton does not exist yet.
- Use this before `l3/lora-scripts-api-training-task` when later execution should reference a user-imported config.

## Load On Demand
- `scripts/import_lora_training_config.py`
