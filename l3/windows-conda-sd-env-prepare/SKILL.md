---
name: windows-conda-sd-env-prepare
description: Atomic capability skill for checking, reusing, or creating local Windows conda environments for ComfyUI and Akegarasu lora-scripts. Use when you need to decide whether an existing env is sufficient, install GPU Torch into it, or produce create-and-install commands for a new env.
---

# Windows Conda SD Env Prepare

## Purpose
Prepare one local Windows conda environment for ComfyUI or lora-scripts.

## Capabilities
- Check whether an existing conda env can be reused.
- Distinguish when ComfyUI and lora-scripts must use separate envs.
- Produce GPU Torch installation commands for a reused env.
- Produce fallback create-and-install commands for a new env.
- Report one chosen env name, Python version target, and core package plan.

## Decision Rules
- Prefer reuse over new creation.
- Do not force ComfyUI and lora-scripts into the same env.
- Prefer Python `3.11` for local ComfyUI.
- Prefer Python `3.10` for local lora-scripts.
- Require `torch.cuda.is_available() == True` before calling the env ready for GPU use.

## Typical Inputs
- Target platform: `ComfyUI` or `lora-scripts`
- Current `conda info --envs` result
- Optional preferred env name

## Typical Outputs
- `reuse` or `create`
- Selected env name
- Required pip install commands

## Route
- Use this before any broad Windows local deploy scene.
- If a reusable env exists but lacks GPU Torch, upgrade that env in place first.
- If no reusable env exists, provide a dedicated env creation path.
