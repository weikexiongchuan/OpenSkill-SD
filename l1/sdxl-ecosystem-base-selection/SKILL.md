---
name: sdxl-ecosystem-base-selection
description: Knowledge skill for comparing SDXL ecosystem families and choosing a LoRA base model. Use when the user needs family differences, compatibility, prompting style, stability, or license-aware base selection before training. Not for training execution.
---

# SDXL Ecosystem Base Selection

## Purpose
Give a decision-ready SDXL family comparison and a base-model recommendation.

## Capabilities
- Compare SDXL Base, Illustrious, NoobAI, Animagine, Pony, and related branches.
- Call out family-specific version-sensitive choices such as `NoobAI XL 0.5` / `Vpred 0.5` / `1.0` / `1.1`.
- Explain compatibility and portability tradeoffs for LoRA training.
- Recommend one primary base and one fallback.
- Call out license or workflow constraints when they matter.

## Typical Inputs
- Target style or dataset
- Deployment checkpoint or target ecosystem
- Commercial or non-commercial usage
- VRAM budget and prompt style tolerance

## Typical Outputs
- Candidate comparison
- Primary base recommendation
- Fallback option
- Training handoff notes

## Route
- Use this skill when the base model is still undecided.
- If the user asks for the latest release status or new checkpoints, verify online first.

## Load On Demand
- `references/model-family-comparison.md`
- `references/lora-base-playbook.md`
- `references/noobai-version-catalog.yaml`
