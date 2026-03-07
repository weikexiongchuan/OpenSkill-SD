# Web Training Schema Structure

## Why This Lives In `l1`
- This topic answers how the web training configuration is structured.
- It is about schema composition, field reuse, and routing rules.
- It does not itself deploy services or execute training tasks.

## Short Answer
- The web platform does **not** use one single flat parameter template.
- It uses one shared backbone plus multiple family-specific schemas.

## Shared Backbone
Most training families reuse grouped blocks from `mikazuki/schema/shared.ts`:
- dataset settings
- save settings
- LR and optimizer settings
- preview image settings
- log settings
- caption settings
- noise settings
- data enhancement
- other options
- precision/cache/batch settings
- distributed training

## Family-Specific Layers
Current main schema families:
- `lora-master.ts`: SD / SDXL LoRA
- `dreambooth.ts`: SD DreamBooth / SDXL full finetune
- `sd3-lora.ts`: SD3 LoRA
- `flux-lora.ts`: Flux LoRA
- `lumina2-lora.ts`: Lumina2 LoRA
- `lora-basic.ts`: simplified form, not the main expert form

## Current Training Family View
Schema-visible `model_train_type` values currently include:
- `sd-lora`
- `sdxl-lora`
- `sd-dreambooth`
- `sdxl-finetune`
- `sd3-lora`
- `flux-lora`
- `lumina-lora`

## Important Mismatch
- `lumina-lora` has a visible schema, but the current backend `/api/run` trainer mapping does not include it.
- `flux-finetune` exists in backend trainer mapping, but no dedicated web schema file is currently exposed for it.

## Routing Rule
- Structural questions stay in `l1`.
- Broad “这个平台能做什么” or deployment questions stay in `l2`.
- Actual API task start / query / terminate belongs in `l3`.
- Detailed per-family parameter filling belongs in `l1/lora-scripts-beginner-parameter-playbook` and is then referenced by `l3` execution skills.
