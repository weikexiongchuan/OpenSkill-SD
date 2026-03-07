---
name: lora-training-sample-prompts-prepare
description: Atomic capability skill for preparing LoRA training sample-image prompts for the current server. Use when training should output sample images and the prompt source must be chosen between random caption samples and user-provided prompts, with a default of 3 sample images.
---

# LoRA Training Sample Prompts Prepare

## Purpose
Prepare one prompt set that makes lora-scripts generate sample images during training.

## Capabilities
- Read the current server workspace and default to the checked dataset runtime path.
- Create one local prompt file for training samples from either random caption files or manual prompts.
- Default to 3 sample images when the user only says `开始` or chooses the recommended path.
- Register the chosen prompt strategy and prompt file into `training/sample-prompts.md`.

## Default Options
- Prompt source choice:
  - `random-captions`：从当前训练集随机选 `3` 条标注生成样图 `（推荐）`
  - `manual`：用用户提供的提示词生成样图
- Output count:
  - default `3`
- Sampler:
  - default `euler_a`
- Steps:
  - default `24`
- CFG:
  - default `7`
- Resolution:
  - default `1024x1024`

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- optional dataset directory override
- one prompt source mode: `random-captions` or `manual`
- optional repeated `--prompt` values for manual mode
- optional prompt count override for random mode

## Typical Outputs
- one local prompt file under `training/sample-prompts/`
- one registry update in `training/sample-prompts.md`
- one `timeline.md` append

## Route
- Use this skill before `l3/lora-training-config-prepare` when training should generate sample images.
- If the dataset has not yet been prepared, switch to `l3/lora-training-dataset-prepare` first.
- If the user chooses manual prompts, accept 1 to 3 prompt lines by default; if they choose the default path, use random 3 captions.
- The generated prompt file should then be passed into `l3/lora-training-config-prepare` so the final config can enable sample images.

## Load On Demand
- `scripts/prepare_lora_sample_prompts.py`
