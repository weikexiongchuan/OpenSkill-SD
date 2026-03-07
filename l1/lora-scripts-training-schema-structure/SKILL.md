---
name: lora-scripts-training-schema-structure
description: Knowledge skill for understanding how lora-scripts web training schemas are organized. Use when the user needs to know whether the web platform uses one shared template or multiple family-specific templates, which training families are currently visible, and how schema structure should route parameter guidance to the beginner playbook. Not for starting training tasks.
---

# LoRA Scripts Training Schema Structure

## Purpose
Explain the schema structure behind lora-scripts web training forms.

## Capabilities
- Explain why this topic belongs to `l1` instead of `l2` or `l3`.
- Summarize whether web training parameters come from one template or a shared backbone plus family-specific overlays.
- List current schema-visible training families and call out important frontend/backend mismatches.
- Provide routing guidance to `l1/lora-scripts-beginner-parameter-playbook` and later execution skills.

## Typical Inputs
- A question about web training form structure
- A target training family such as `sd-lora`, `flux-lora`, or `sd3-lora`
- A need to decide how later parameter guidance should route

## Typical Outputs
- One schema-structure summary
- Shared-vs-specialized field breakdown
- Current family/mismatch note
- Handoff note to later execution skills

## Route
- Use this skill when the question is about parameter structure, schema families, or configuration architecture.
- Keep this in `l1` because it is definition and protocol knowledge, not a user-facing deployment scene and not an execution action.
- If the user wants to know how to fill the actual beginner parameters, switch to `l1/lora-scripts-beginner-parameter-playbook`.
- If the user wants to actually start training by API, switch to `l3/lora-scripts-api-training-task` after config is ready.

## Load On Demand
- `references/web-training-schema-structure.md`
