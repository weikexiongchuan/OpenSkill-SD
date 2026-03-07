---
name: lora-scripts-api-training-task
description: Atomic capability skill for starting, querying, and terminating lora-scripts training tasks through the web API. Use when a final JSON config payload is already prepared and the task should be launched via `/api/run`, queried via `/api/tasks`, or terminated via `/api/tasks/terminate/{task_id}`. Not for deciding detailed per-family parameter values.
---

# LoRA Scripts API Training Task

## Purpose
Drive lora-scripts training task lifecycle through its HTTP API.

## Capabilities
- Start one training task via `POST /api/run`.
- Query current tasks via `GET /api/tasks`.
- Terminate one task via `GET /api/tasks/terminate/{task_id}`.
- For SDXL-family runs, prefetch tokenizer dependencies before the first real start when needed.
- Monitor startup until the task is still `RUNNING` and TensorBoard event files actually appear.
- Reuse one local script instead of rewriting ad-hoc `curl` commands.

## Typical Inputs
- API base URL such as `http://127.0.0.1:28000`
- One finalized JSON config payload file for `/api/run`
- Optional task id for terminate
- Optional startup monitor timeout when the caller wants confirmation instead of fire-and-forget

## Typical Outputs
- API response JSON
- Started task id or error message
- Current task list
- Termination result
- Confirmed startup signal: task still `RUNNING` plus TensorBoard event file present

## Route
- Use this skill when the user explicitly wants to start or manage a training task through the lora-scripts web API.
- Do not guess missing training fields. Expect a finalized config payload.
- If the user is still deciding schema family or parameter structure, switch to `l1/lora-scripts-training-schema-structure` first.
- If the user still needs beginner-friendly parameter filling guidance, switch to `l1/lora-scripts-beginner-parameter-playbook` before execution.
- If the config still does not bind the current server's base model path, dataset directory, or output name, switch to `l3/lora-training-config-prepare` first.
- If the config still contains numeric-looking strings such as `1e-4`, `1`, or `8~10`, normalize them first through `l3/lora-training-config-prepare` before API execution.
- For SDXL-family runs, do not treat the API `success` response alone as completion; continue until tokenizer warmup is done, the task remains `RUNNING`, and TensorBoard event files appear.
- After a task is started, refreshed, finished, failed, or terminated, sync the run status back through `l3/lora-training-state-record-update` when the local server workspace is in use.

## Load On Demand
- `references/http-contract.md`
- `scripts/lora_scripts_api_train.py`
- `scripts/run_remote_lora_training_start.py`
