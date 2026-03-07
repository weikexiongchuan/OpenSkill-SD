---
name: lora-training-diagnosis-playbook
description: Official-source playbook for diagnosing drawing-model LoRA dataset quality, config sanity, domain mismatch risk, and training-progress signals in lora-scripts or sd-scripts based runs. Use when you need to reason about why a LoRA run failed to start, has weak trigger stability, lacks observability, looks underfit or overfit, or may have data-caption mismatch risk.
---

# LoRA Training Diagnosis Playbook

## Purpose
Provide a low-token diagnosis rubric for LoRA training issues using official upstream training docs.

## Covers
- Dataset and caption structure signals that directly affect training quality.
- Config interactions that can silently disable expected behavior.
- Domain mismatch risk between `二次元 / 标签型` and `三次元 / 自然语言型` data.
- Training-progress signals that are safe to judge from logs and TensorBoard.
- A clean split between confirmed issues and explicit inference.

## Route
- Use this skill when the user asks why LoRA training failed, why效果不稳, why TensorBoard has no useful data, or which data/config issue is most likely.
- Prefer the official-source rubric in `references/official-diagnosis-rubric.md`.
- If one concrete server run should be analyzed, pair this skill with `l3/lora-training-analysis`.
- If the dataset itself is still unchecked, run `l3/lora-training-dataset-prepare` first.
- If the config is not yet bound to the current server, run `l3/lora-training-config-prepare` first.

## Load On Demand
- `references/official-diagnosis-rubric.md`
