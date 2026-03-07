---
name: autodl-lora-scripts-deploy-screen
description: Scenario skill for deploying, exposing, upgrading, and recovering Akegarasu lora-scripts GUI on AutoDL with screen-managed sessions. Use when the user goal is a broad lora-scripts outcome such as deploy, start, restart, expose, or fix the training GUI rather than a single low-level command.
---

# AutoDL LoRA Scripts Deploy Screen

## Purpose
Handle the end-to-end lora-scripts GUI deployment scenario on AutoDL.

## User-Facing Policy
- Before the first user-facing reply, load `../references/user-facing-scenario-interaction.md`.
- Default to beginner-friendly, automation-first interaction unless the user explicitly wants detailed explanations.
- User-facing capability metadata is maintained centrally in `../references/scene-registry.yaml`; do not duplicate it here.

## First Move
- Before any SSH, install, or restart action, inspect the current local workspace for this server.
- Read only `<workspace-root>/servers/<server-alias>/state.md` and `login/method.md` first.
- If the user is onboarding their own server and it is not yet clear whether this is a new or previously used server, ask that first in user-facing Chinese.
- Use that state to classify the request as first server tracking, first lora-scripts deployment, existing deployment restart/recovery, or upgrade.
- If the local workspace does not exist yet, use `l3/local-server-state-workspace-init` before continuing.

## Scenario Defaults
- Treat this skill as direct remote execution on AutoDL once SSH access is available.
- Default server root: `/root/autodl-tmp`
- Default app dir: `/root/autodl-tmp/lora-scripts/app`
- Default `screen` session: `lora-scripts-main`
- Default internal/tunnel port: `28000`
- Default tensorboard port: `6016`
- Access mode must still be confirmed; for `public-port`, prefer `6006` and fall back to `6008`.

## Scenario Scope
- Check whether lora-scripts already exists and whether it can start directly.
- When the user asks what this web platform can train, answer that at the scene layer first and only dive into deeper structure or execution skills when needed.
- When the user asks how to fill training parameters, answer briefly at the scene layer first and then hand off to the beginner parameter playbook if deeper guidance is needed.
- When the user only says they want to train, offer template choices first instead of leading with custom parameter explanation; default to conservative starters before standard templates.
- When the user wants to train but the scene is still unclear, first confirm one scene choice from `角色 / 画风 / 服装配饰` before template choice, dataset prep, config binding, or API start.
- Confirm one access choice with the user, but explain it in plain Chinese first instead of raw terms.
- Whenever this scenario asks the user to choose, list all options for that step and mark the default path as `（推荐）`.
- If the user only replies `开始`、`直接开始`、`按默认`, or `用推荐的`, continue with the current recommended default without repeating the question.
- Keep the user-facing wording brief and colloquial; prefer one short sentence.
- Install or update only when needed.
- Start, stop, restart, and health-check the GUI in `screen`.
- When the user asks why the current LoRA run failed, why数据学不住, or why TensorBoard/日志看起来不对, switch to `l3/lora-training-analysis` and use `l1/lora-training-diagnosis-playbook` as the reasoning rubric.
- Record service state and training state back into the local markdown workspace when training-related actions happen.
- If the current task depends on a base model, dataset, or custom config, tell the user at deploy start what to upload into AutoDL 文件存储 first; after deployment, fetch only the chosen assets or switch to `l3/lora-basemodel-download` when the user chooses the download-script branch.
- If the user already has a custom config file, import it into the server workspace first and mark it as `manual-import`.
- Before training starts, if the dataset is local or not yet checked, run `l3/lora-training-dataset-prepare` first. If the platform supports sample images, confirm the sample prompt source next, default to random 3 captions through `l3/lora-training-sample-prompts-prepare`, and then bind the current server's base model path, dataset directory, output name, and sample prompt file into one prepared runnable config.

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
- `l1/lora-scripts-training-schema-structure`
- `l1/lora-scripts-beginner-parameter-playbook`
- `l1/lora-training-diagnosis-playbook`
- `l3/ssh-server-connect`
- `l3/local-server-state-workspace-init`
- `l3/local-server-state-record-update`
- `l3/autodl-remote-workspace-init`
- `l3/autodl-host-facts-collect`
- `l3/screen-session-manage`
- `l3/proxy-env-manage`
- `l3/autodl-academic-model-download-acceleration`
- `l3/lora-basemodel-download`
- `l3/lora-training-dataset-prepare`
- `l3/lora-training-sample-prompts-prepare`
- `l3/lora-training-analysis`
- `l3/lora-scripts-api-training-task`
- `l3/lora-training-state-record-update`
- `l3/lora-training-config-import`
- `l3/lora-training-config-prepare`

## Layer Split In This Scenario
- `l1` defines the workspace schema and record-update rules.
- `l2` decides the branch: first deploy, restart, recover, expose, or upgrade.
- `l3` performs the concrete remote actions and local state writes.

## Route
- Start here when the request is broadly “deploy or start lora-scripts on AutoDL”, “deploy or start LoRA training GUI on AutoDL”, “this web platform supports what training families”, “I want to train a LoRA here”, or “help me diagnose this LoRA training problem”.
- First inspect the local workspace state before deciding any remote action.
- When the user is connecting a server and its history is not yet obvious, first ask `这是新服务器，还是之前用过的那台？`, then map the answer to first tracking vs existing-state flow.
- If the workspace is missing, initialize it first; if state already shows an existing lora-scripts deployment, prefer verify/restart/recover before reinstall.
- Confirm the exposure choice before final handoff, but ask in user-facing Chinese with the differences explained; only map it back to `public-port`, `ssh-tunnel-cli`, or `ssh-tunnel-gui` internally.
- Use `l1/` only when schema or state semantics are unclear; use `l3/` only for the next concrete action.
- If the user only asks for one precise action such as “verify key login”, “check host facts”, “import my custom training config”, “bind base model and dataset into my config”, or “start training through the web API”, jump directly to the matching `l3/` skill.

## Load On Demand
- Do not preload every reference file.
- `../references/user-facing-scenario-interaction.md`
- `../references/scene-registry.yaml`
- `references/lora-scripts-operations.md`
- `references/lora-scripts-troubleshooting.md`
- `references/lora-scripts-api-capability.md`
- `references/access-mode-and-compliance.md`
- `../references/autodl-storage-and-asset-flow.md`

Load only the file that matches the next blocker:
- `../references/user-facing-scenario-interaction.md` before the first user-facing reply in this scenario.
- `../references/scene-registry.yaml` only when the user asks what you can do or when user-facing scene capability aggregation is needed.
- `references/lora-scripts-operations.md` for install, update, start, restart, or health-check flow.
- `references/lora-scripts-troubleshooting.md` only when start-up or API checks fail.
- `references/lora-scripts-api-capability.md` when the user asks what training types the web UI supports, whether schemas are unified, or whether training can be started by API.
- `../../l1/lora-training-diagnosis-playbook/references/official-diagnosis-rubric.md` when the user asks why training failed, why data quality may be insufficient, or how to interpret logs/TensorBoard.
- `../../l1/lora-scripts-training-schema-structure/references/web-training-schema-structure.md` only when the question shifts from scene answer to schema-architecture explanation.
- `../../l1/lora-scripts-beginner-parameter-playbook/references/training-templates.yaml` first when the user broadly asks to train and needs template options.
- `../../l1/lora-scripts-beginner-parameter-playbook/references/parameter-dictionary.md` or sibling references only when the question shifts to actual parameter filling, beginner values, or style/character/outfit recipes.
- `references/access-mode-and-compliance.md` only when choosing exposure mode.
- `../references/autodl-storage-and-asset-flow.md` when current deployment needs base models, datasets, custom configs, or storage-budget planning.
