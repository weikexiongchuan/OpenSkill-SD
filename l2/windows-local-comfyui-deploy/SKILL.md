---
name: windows-local-comfyui-deploy
description: Scenario skill for deploying, starting, restarting, and recovering ComfyUI on a local Windows machine. Use when the user wants a broad local ComfyUI outcome rather than a single pip or python command.
---

# Windows Local ComfyUI Deploy

## Purpose
Handle the end-to-end ComfyUI deployment scenario on a local Windows machine.

## First Move
- Before any install or restart action, inspect the current workspace root and check whether the target app directory already exists.
- Check the available conda environments first and prefer reuse over creating a new one.
- Use `l3/windows-conda-sd-env-prepare` before deciding whether the current machine can reuse an existing Python environment.

## Scenario Defaults
- Treat this skill as direct execution on the local Windows machine, not AutoDL.
- Default app dir: `<workspace-root>/ComfyUI`
- Default log file: `<workspace-root>/comfyui.log`
- Default local URL: `http://127.0.0.1:8188`
- Default host: `127.0.0.1`
- Default port: `8188`
- Preferred reusable conda env: a Python `3.11` env with GPU Torch already available.

## Scenario Scope
- Check whether ComfyUI code already exists and whether it can start directly.
- Reuse an existing conda env when it already has a compatible Python version and can be upgraded in place without conflicting with `lora-scripts`.
- Keep ComfyUI in its own Python environment instead of sharing one with `lora-scripts`, because their `transformers` requirements can diverge.
- Install or update only when needed.
- Start, stop, restart, and health-check the local service.
- When the user asks which first checkpoint to download right after ComfyUI becomes usable, prefer one `WAI`-prefixed Illustrious checkpoint before broader family comparison.
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
- `l3/windows-conda-sd-env-prepare`
- `l3/windows-local-model-download`

## Route
- Start here when the request is broadly “在 Windows 本地部署 ComfyUI”, “帮我启动本地 ComfyUI”, “恢复本地 ComfyUI”.
- First decide whether the local machine can reuse an existing conda env.
- If the app dir already exists, prefer verify/restart/recover before reinstall.
- If the user only asks for one precise action such as “给我环境创建命令” or “检查本地端口”, jump directly to the matching `l3/` skill or direct command.

## Load On Demand
- `references/windows-comfyui-operations.md`
- `references/windows-comfyui-troubleshooting.md`

Load only the file that matches the next blocker:
- `references/windows-comfyui-operations.md` for install, update, start, restart, or health-check flow.
- `references/windows-comfyui-troubleshooting.md` only when start-up or GPU checks fail.
