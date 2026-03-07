---
name: lora-training-analysis
description: Atomic capability skill for analyzing one LoRA dataset and/or one concrete training run from the local AutoDL workspace. Use when you need a structured diagnosis from dataset registry, prepared config, API status, remote logs, and TensorBoard event presence, and want the result written back into `training/analysis.md`.
---

# LoRA Training Analysis

## Purpose
Turn one LoRA run into a concise diagnosis report.

## Capabilities
- Read the current server workspace and locate the active dataset, config, and run.
- Check for confirmed blockers from dataset stats, config conflicts, API status, logs, and TensorBoard event files.
- Mark loss-trend or template-fit judgments as explicit inference instead of hard facts.
- Write one latest analysis plus history into `training/analysis.md`.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- optional run name override
- optional app dir override
- optional API base URL override
- optional `--local-only` when remote SSH check is not available

## Typical Outputs
- one diagnosis summary on stdout
- one markdown report in `training/analysis.md`
- one `timeline.md` append for traceability

## Route
- Read `state.md` and `login/method.md` first.
- Use `l1/lora-training-diagnosis-playbook` for the reasoning rubric.
- If the dataset has not yet been checked, switch to `l3/lora-training-dataset-prepare` first.
- If the training config is not yet prepared for the current server, switch to `l3/lora-training-config-prepare` first.
- If password login is in use and remote inspection is needed, export `SSH_PASSWORD` for this command; never write the plaintext password into local workspace files.

## Load On Demand
- `../../l1/lora-training-diagnosis-playbook/references/official-diagnosis-rubric.md`
- `scripts/run_remote_lora_training_analysis.py`
