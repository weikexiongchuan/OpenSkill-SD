---
name: lora-training-config-prepare
description: Atomic capability skill for finalizing one LoRA training config for the current server by binding the required base model path, train data directory, and output name. Use after a built-in template is chosen or a manual-import config is available, and before starting training through the lora-scripts API.
---

# LoRA Training Config Prepare

## Purpose
Turn one imported or template-derived config into a server-ready runnable config.

## Capabilities
- Load one JSON config, JSON history preset, or TOML config.
- Bind the required `pretrained_model_name_or_path`, `train_data_dir`, and `output_name`.
- Optionally attach one sample-image prompt file so training can output preview images by default.
- Optionally set `output_dir`.
- Normalize numeric-looking strings such as `1e-4`, `1`, or `8~10` into runnable numeric values.
- Write one normalized runnable JSON file under `training/prepared-configs/`.
- Register the prepared config in `training/configs.md` and append `timeline.md`.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- one source config file path
- base model path
- training data directory
- output name
- optional prepared config name override
- optional preset name when the source is a JSON history file
- optional output dir and note
- optional sample prompt file and sample image cadence

## Typical Outputs
- one prepared JSON config under the target server workspace
- updated `training/configs.md`
- appended `timeline.md`

## Route
- Use this skill after template selection or manual config import, and before `l3/lora-scripts-api-training-task`.
- If training should produce sample images, prepare the prompt file first through `l3/lora-training-sample-prompts-prepare` and pass it here.
- If the dataset path is still local-only or has not passed image+txt pairing / 64-multiple checks, use `l3/lora-training-dataset-prepare` first.
- Use `l3/local-server-state-workspace-init` first if the workspace skeleton does not exist yet.
- If the user only has a raw custom config file, use `l3/lora-training-config-import` first so the original file is preserved and marked as `manual-import`.

## Load On Demand
- `scripts/materialize_lora_training_template.py` when a built-in beginner template must first become a source config
- `scripts/prepare_lora_training_config.py`
