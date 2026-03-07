---
name: autodl-comfyui-deploy-screen
description: Scenario skill for deploying, exposing, upgrading, and recovering ComfyUI on AutoDL with screen-managed sessions. Use when the user goal is a broad ComfyUI outcome such as deploy, start, restart, expose, or fix ComfyUI rather than a single low-level command.
---

# AutoDL ComfyUI Deploy Screen

## Purpose
Handle the end-to-end ComfyUI deployment scenario on AutoDL.

## User-Facing Policy
- Before the first user-facing reply, load `../references/user-facing-scenario-interaction.md`.
- Default to beginner-friendly, automation-first interaction unless the user explicitly wants detailed explanations.
- User-facing capability metadata is maintained centrally in `../references/scene-registry.yaml`; do not duplicate it here.

## First Move
- Before any SSH, install, or restart action, inspect the current local workspace for this server.
- Read only `<workspace-root>/servers/<server-alias>/state.md` and `login/method.md` first.
- If the user is onboarding their own server and it is not yet clear whether this is a new or previously used server, ask that first in user-facing Chinese.
- Use that state to classify the request as first server tracking, first ComfyUI deployment, existing deployment restart/recovery, or upgrade.
- If the local workspace does not exist yet, use `l3/local-server-state-workspace-init` before continuing.

## Scenario Defaults
- Treat this skill as direct remote execution on AutoDL once SSH access is available.
- Default server root: `/root/autodl-tmp`
- Default app dir: `/root/autodl-tmp/comfyui/app`
- Default `screen` session: `comfyui-main`
- Default internal/tunnel port: `8188`
- Access mode must still be confirmed; for `public-port`, prefer `6006` and fall back to `6008`.

## Scenario Scope
- Check whether ComfyUI already exists and whether it can start directly.
- Confirm one access choice with the user, but explain it in plain Chinese first instead of raw terms.
- Whenever this scenario asks the user to choose, list all options for that step and mark the default path as `（推荐）`.
- If the user only replies `开始`、`直接开始`、`按默认`, or `用推荐的`, continue with the current recommended default without repeating the question.
- Keep the user-facing wording brief and colloquial; prefer one short sentence.
- Install or update only when needed.
- Start, stop, restart, and health-check the service in `screen`.
- Record service state back into the local markdown workspace.
- If current deployment depends on models or workflow assets, tell the user at deploy start what to upload into AutoDL 文件存储 first, then fetch only the chosen assets after deployment or on explicit instruction.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- Optional install directory override
- Optional session name override
- Access mode choice and optional port override
- Optional public URL or tunnel target

## Typical Outputs
- One usable service URL
- Session name and port choice
- Updated local state record

## Compose With
- `l1/autodl-local-server-state-workspace`
- `l3/ssh-server-connect`
- `l3/local-server-state-workspace-init`
- `l3/local-server-state-record-update`
- `l3/autodl-remote-workspace-init`
- `l3/autodl-host-facts-collect`
- `l3/screen-session-manage`
- `l3/proxy-env-manage`
- `l3/autodl-academic-model-download-acceleration`

## Layer Split In This Scenario
- `l1` defines the workspace schema and record-update rules.
- `l2` decides the branch: first deploy, restart, recover, expose, or upgrade.
- `l3` performs the concrete remote actions and local state writes.

## Route
- Start here when the request is broadly “deploy or start ComfyUI on AutoDL”.
- First inspect the local workspace state before deciding any remote action.
- When the user is connecting a server and its history is not yet obvious, first ask `这是新服务器，还是之前用过的那台？`, then map the answer to first tracking vs existing-state flow.
- If the workspace is missing, initialize it first; if state already shows an existing ComfyUI deployment, prefer verify/restart/recover before reinstall.
- Confirm the exposure choice before final handoff, but ask in user-facing Chinese with the differences explained; only map it back to `public-port`, `ssh-tunnel-cli`, or `ssh-tunnel-gui` internally.
- Use `l1/` only when schema or state semantics are unclear; use `l3/` only for the next concrete action.
- If the user only asks for one precise action such as “check network turbo” or “verify key login”, jump directly to the matching `l3/` skill.

## Load On Demand
- Do not preload every reference file.
- `../references/user-facing-scenario-interaction.md`
- `../references/scene-registry.yaml`
- `references/comfyui-operations.md`
- `references/comfyui-troubleshooting.md`
- `references/autodl-port-mapping.md`
- `references/access-mode-and-compliance.md`
- `../references/autodl-storage-and-asset-flow.md`
- `references/comfyui-prompt-playbook.md`
- `references/comfyui-field-validated-notes.md`

Load only the file that matches the next blocker:
- `../references/user-facing-scenario-interaction.md` before the first user-facing reply in this scenario.
- `../references/scene-registry.yaml` only when the user asks what you can do or when user-facing scene capability aggregation is needed.
- `references/comfyui-operations.md` for install, update, start, restart, or health-check flow.
- `references/comfyui-troubleshooting.md` only when start-up or API checks fail.
- `references/autodl-port-mapping.md` and `references/access-mode-and-compliance.md` only when choosing exposure mode.
- `../references/autodl-storage-and-asset-flow.md` when current deployment needs model files, workflow assets, or storage-budget planning.
- `references/comfyui-prompt-playbook.md` only after the service is already usable.
- `references/comfyui-field-validated-notes.md` only when AutoDL behavior differs from the expected workflow.
