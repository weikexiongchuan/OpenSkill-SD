---
name: windows-local-lora-scripts-deploy
description: Scenario skill for deploying, starting, restarting, and recovering Akegarasu lora-scripts GUI on a local Windows machine. Use when the user wants a broad local lora-scripts outcome rather than a single pip or python command.
---

# Windows Local LoRA Scripts Deploy

## Purpose
Handle the end-to-end lora-scripts GUI deployment scenario on a local Windows machine.

## First Move
- Before any install or restart action, inspect the current workspace root and check whether the target app directory already exists.
- Check the available conda environments first and prefer reuse over creating a new one.
- Use `l3/windows-conda-sd-env-prepare` before deciding whether the current machine can reuse an existing Python environment.

## Scenario Defaults
- Treat this skill as direct execution on the local Windows machine, not AutoDL.
- Default app dir: `<workspace-root>/lora-scripts`
- Default log file: `<workspace-root>/lora-scripts.log`
- Default local URL: `http://127.0.0.1:28000`
- Default host: `127.0.0.1`
- Default port: `28000`
- Default tag editor port: `28001`
- Default tensorboard port: `6006`
- Preferred reusable conda env: a Python `3.10` env with GPU Torch already available.

## Scenario Scope
- Check whether lora-scripts code and its required submodules already exist and whether the GUI can start directly.
- Reuse an existing Python `3.10` conda env when possible.
- Keep lora-scripts in its own Python environment instead of sharing one with ComfyUI.
- Install `xformers`, fixed GUI requirements, and only then start the local GUI.
- When the user asks what this local training GUI can train, answer at the scene layer first and only dive into `l1` or API skills when needed.
- Report one usable local URL, one env choice, and one log path.

## Typical Inputs
- `<workspace-root>`
- Optional conda env name override
- Optional app directory override
- Optional local port override

## Typical Outputs
- One usable local URL
- One selected conda env
- One start command and one health-check result

## Compose With
- `l1/lora-scripts-training-schema-structure`
- `l1/lora-scripts-beginner-parameter-playbook`
- `l1/lora-training-diagnosis-playbook`
- `l3/windows-conda-sd-env-prepare`
- `l3/lora-scripts-api-training-task`
- `l3/lora-training-analysis`

## Route
- Start here when the request is broadly “在 Windows 本地部署 lora-scripts”, “帮我启动本地 LoRA 训练 GUI”, “恢复本地 lora-scripts”.
- First decide whether the local machine can reuse an existing conda env.
- If the app dir already exists, prefer verify/restart/recover before reinstall.
- If the user later asks about parameter filling or diagnosis, hand off to the existing `l1` / `l3` skills instead of duplicating those details here.

## Load On Demand
- `references/windows-lora-scripts-operations.md`
- `references/windows-lora-scripts-troubleshooting.md`

Load only the file that matches the next blocker:
- `references/windows-lora-scripts-operations.md` for install, update, start, restart, submodule repair, or health-check flow.
- `references/windows-lora-scripts-troubleshooting.md` only when start-up, GUI, submodule, or package checks fail.
