---
name: lora-scripts-beginner-parameter-playbook
description: Knowledge skill for beginner-friendly lora-scripts training parameter guidance. Use when the user needs a small-core parameter dictionary, model-family starter values, domain-aware starter values for 二次元 or 三次元 training, or scenario recipes for style, character, and clothing/accessory LoRA training in the lora-scripts web platform. Not for executing API tasks.
---

# LoRA Scripts Beginner Parameter Playbook

## Purpose
Give a beginner-friendly parameter dictionary and starter settings for lora-scripts web training.

## Capabilities
- Explain only the small set of training parameters a beginner usually needs to touch.
- Give starter values by training family such as `sd-lora`, `sdxl-lora`, `sd3-lora`, `flux-lora`, and `lumina-lora`.
- Give one extra domain overlay for `二次元 / 标签型底模` and `三次元 / 写实自然语言型底模`.
- Provide a template catalog that the scene layer can offer first when the user simply says they want to train.
- Preserve archived real-world configs for later comparison and template refinement.
- Give scenario recipes for `画风训练`、`角色训练`、`服装/配饰训练`.
- Separate direct official facts from inferred beginner recommendations.

## Typical Inputs
- One target training family
- One target domain such as `二次元` or `三次元`
- One target scenario such as style, character, or outfit/accessory
- VRAM level or whether the user wants safer defaults

## Typical Outputs
- Core parameter dictionary
- One family starter profile
- One domain overlay
- One scenario recipe
- Handoff note for API execution

## Route
- Use this skill when the user asks how to fill lora-scripts training parameters in a beginner-friendly way.
- Keep this in `l1` because it is parameter knowledge and fill-in guidance, not scene orchestration and not task execution.
- If the user asks about schema structure rather than parameter filling, switch to `l1/lora-scripts-training-schema-structure`.
- If the user wants to judge whether data and captions are mismatched for the chosen domain, also read `l1/lora-training-diagnosis-playbook`.
- If the user wants to actually send the training task after config is ready, switch to `l3/lora-scripts-api-training-task`.
- If the user asks for the latest recommendations or new model-family support, verify against official upstream docs online first.

## Load On Demand
- `references/training-templates.yaml`
- `references/template-positioning.md`
- `references/saved-config-catalog.yaml`
- `references/parameter-dictionary.md`
- `references/model-family-starters.md`
- `references/domain-2d-vs-3d.md`
- `references/scenario-recipes.md`
