# State File Templates

## state.md
```markdown
# Server State: <server-alias>

## Connection
- Host: <host>
- Port: <port>
- User: <user>

## Login Mode
- Method: <key|password>
- Identity File: <path-or-empty>
- SSH Alias: <alias-or-empty>

## Runtime
- Workspace Root: <remote-workspace-root>
- Last Verified: <iso-time>
- Status: <active|inactive|unknown>
```

## login/method.md
```markdown
# Login Method

- Method: <key|password>
- Password Stored: no
- Identity File: <path-or-empty>
- SSH Alias: <alias-or-empty>
- Updated At: <iso-time>
```

## services/comfyui.md
```markdown
# ComfyUI Service

- Session: <screen-session>
- Internal Port: <port>
- Access Mode: <public-port|ssh-tunnel-cli|ssh-tunnel-gui>
- Service URL: <url-or-empty>
- Health: <ok|failed|unknown>
- Updated At: <iso-time>
```

## services/lora-scripts.md
```markdown
# LoRA Scripts Service

- Session: <screen-session>
- Service Port: <port>
- Tensorboard Port: <port>
- Access Mode: <public-port|ssh-tunnel-cli|ssh-tunnel-gui>
- Service URL: <url-or-empty>
- Health: <ok|failed|unknown>
- Updated At: <iso-time>
```

## storage/large-files.md
```markdown
# Large File Registry

## Current Files
- id=<asset-id> | kind=<basemodel|dataset|output|cache|other> | label=<label> | tier=<fs|tmp|pub|other> | status=<planned|downloaded|linked|failed|manual-upload|unknown> | source=<hf-mirror|manual-upload|generated|other> | stored=<absolute-path-or-empty> | runtime=<absolute-path-or-empty> | notes=<free-text-or-empty>

## History
- <iso-time> | id=<asset-id> | kind=<asset-kind> | tier=<storage-tier> | status=<status> | source=<source> | stored=<absolute-path>
```

## training/lora.md
```markdown
# LoRA Training State

## Active Run
- Run Name: <run-name-or-empty>
- Template ID: <template-id-or-empty>
- Scenario: <style|character|outfit-accessory|other>
- Model Train Type: <sd-lora|sdxl-lora|sd3-lora|flux-lora|lumina-lora|other>
- Status: <template-selected|queued|running|finished|failed|terminated|unknown>
- Task ID: <task-id-or-empty>
- API Base URL: <url-or-empty>
- Output Name: <output-name-or-empty>
- Output Dir: <absolute-output-dir-or-empty>
- Resume Checkpoint: <path-or-empty>
- Notes: <free-text-or-empty>
- Updated At: <iso-time>

## Registered Runs
- <iso-time> | run=<run-name> | template=<template-id> | scenario=<scene> | model=<model-train-type> | status=<status> | task=<task-id> | output=<output-name> | output_dir=<absolute-output-dir-or-empty>
```

## training/models.md
```markdown
# LoRA Base Model Registry

## Latest Model
- Slot ID: <slot-id-or-empty>
- Label: <model-label-or-empty>
- Family: <noobai|illustrious|other|empty>
- Family Version: <exact-version-or-empty>
- Family Branch: <epsilon|vpred|standard|guided|other|empty>
- Repo ID: <hf-repo-id-or-empty>
- Filename: <model-file-name-or-empty>
- Download Mode: <hf-mirror|huggingface|manual-upload|pub-copy|other|empty>
- Storage Tier: <fs|tmp|pub|other|empty>
- Stored Path: <absolute-path-or-empty>
- Active Path: <absolute-path-or-empty>
- Status: <planned|downloaded|linked|failed|manual-upload|unknown>
- Notes: <free-text-or-empty>
- Updated At: <iso-time>

## Registered Models
- <iso-time> | slot=<slot-id> | family=<family> | version=<version> | branch=<branch> | status=<status> | mode=<download-mode> | file=<filename> | path=<stored-path>
```

## training/datasets.md
```markdown
# LoRA Training Dataset Registry

## Latest Dataset
- Dataset ID: <dataset-id-or-empty>
- Label: <dataset-label-or-empty>
- Source: <local-upload|remote-existing|manual-upload|other>
- Storage Tier: <fs|tmp|pub|other|empty>
- Stored Path: <absolute-path-or-empty>
- Runtime Path: <absolute-path-or-empty>
- Status: <ready|prepared|needs-captions|needs-size-fix|failed|unknown>
- Size Policy: <crop|pad-white|check-only|empty>
- Image Count: <number-or-empty>
- Caption Count: <number-or-empty>
- Paired Count: <number-or-empty>
- Missing Caption Count: <number-or-empty>
- Orphan Caption Count: <number-or-empty>
- Duplicate Image Key Count: <number-or-empty>
- Duplicate Caption Key Count: <number-or-empty>
- Multiple Of 64 OK Count: <number-or-empty>
- Needs Resize Count: <number-or-empty>
- Resized Count: <number-or-empty>
- Resize Error Count: <number-or-empty>
- Notes: <free-text-or-empty>
- Updated At: <iso-time>

## Registered Datasets
- <iso-time> | id=<dataset-id> | status=<status> | source=<source> | images=<count> | paired=<count> | missing=<count> | orphan=<count> | resized=<count> | size=<policy> | path=<runtime-path>
```

## training/configs.md
```markdown
# LoRA Training Config Registry

## Latest Config
- Config Name: <config-name-or-empty>
- Source: <manual-import|prepared|other>
- Stage: <imported|prepared>
- File Type: <toml-config|json-config|json-history|raw-file>
- Parse Status: <parsed|raw-copy>
- Original Path: <absolute-local-path-or-empty>
- Stored Path: <training/imported-configs/...|absolute-path-or-empty>
- Prepared Path: <training/prepared-configs/...|empty>
- Selected Preset: <preset-name-or-empty>
- Model Train Type: <sd-lora|sdxl-lora|sd3-lora|flux-lora|lumina-lora|other|empty>
- Base Model Path: <path-or-empty>
- Train Data Dir: <path-or-empty>
- Output Name: <output-name-or-empty>
- Notes: <free-text-or-empty>
- Updated At: <iso-time>

## Registered Configs
- <iso-time> | name=<config-name> | source=<manual-import|prepared|other> | stage=<imported|prepared> | type=<file-type> | model=<model-train-type> | output=<output-name> | preset=<preset-name-or-empty> | file=<relative-path>
```

## training/sample-prompts.md
```markdown
# LoRA Sample Prompt Registry

## Latest Prompt Set
- Prompt Set Name: <name-or-empty>
- Source: <random-captions|manual>
- Prompt Count: <number-or-empty>
- Dataset Dir: <remote-dataset-path-or-empty>
- File Path: <training/sample-prompts/...|absolute-path-or-empty>
- Sample Width: <number-or-empty>
- Sample Height: <number-or-empty>
- Sample CFG: <number-or-empty>
- Sample Steps: <number-or-empty>
- Sample Seed Base: <number-or-empty>
- Sample Sampler: <sampler-or-empty>
- Notes: <free-text-or-empty>
- Updated At: <iso-time>

## Prompt Preview
- 1: <prompt-preview>

## History
- <iso-time> | name=<name> | source=<source> | count=<count> | sampler=<sampler> | file=<relative-path>
```

## training/analysis.md
```markdown
# LoRA Training Analysis

## Latest Analysis
- Run Name: <run-name-or-empty>
- Scope: <dataset+config|dataset+config+runtime>
- Overall Status: <healthy|needs-attention|blocked|unknown>
- Data Status: <ok|needs-fix|unknown>
- Runtime Status: <RUNNING|FINISHED|FAILED|unknown>
- Current Step: <number-or-empty>
- Total Steps: <number-or-empty>
- Progress Percent: <number-or-empty>
- Latest Average Loss: <number-or-empty>
- Validation Signal: <configured|not-configured|unknown>
- TensorBoard Event Count: <number-or-empty>
- Primary Finding: <short-summary>
- Suggested Action: <short-next-step>
- Notes: <free-text-or-empty>
- Updated At: <iso-time>

## Confirmed Findings
- [<severity>] <finding>

## Inferred Risks
- [<severity>] <risk>

## Suggested Actions
- <action>

## History
- <iso-time> | run=<run-name> | status=<overall-status> | data=<data-status> | runtime=<runtime-status> | finding=<primary-finding>
```

## timeline.md
```markdown
# Timeline

- <iso-time> initialized server state.
- <iso-time> updated login mode to <key|password>.
- <iso-time> updated ComfyUI or lora-scripts URL and health state.
```
