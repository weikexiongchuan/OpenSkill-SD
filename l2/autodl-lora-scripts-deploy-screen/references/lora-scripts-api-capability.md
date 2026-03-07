# LoRA Scripts API Capability

## Scope
This note is for judging what the lora-scripts web platform can drive through its own HTTP API, instead of by manual browser clicks.

## Key Findings
- The web backend is `FastAPI`, started by `gui.py`, and mounts API routes under `/api`.
- Training start is exposed by `POST /api/run`.
- Task query is exposed by `GET /api/tasks`.
- Task termination is exposed by `GET /api/tasks/terminate/{task_id}`.
- Schema query is exposed by `GET /api/schemas/all` and `GET /api/schemas/hashes`.
- Preset query is exposed by `GET /api/presets`.

## Training Types
Count training support from two layers separately because frontend schema and backend trainer mapping are not fully aligned.

### Schema-Visible Training Types
These `model_train_type` values are declared in `mikazuki/schema/*.ts` and therefore can appear as web-form training modes:
- `sd-lora`
- `sdxl-lora`
- `sd-dreambooth`
- `sdxl-finetune`
- `sd3-lora`
- `flux-lora`
- `lumina-lora`

Count: `7`

### API-Mapped Runnable Training Types
These `model_train_type` values are accepted by backend `trainer_mapping` in `mikazuki/app/api.py` and can be mapped to a trainer script by `POST /api/run`:
- `sd-lora`
- `sdxl-lora`
- `sd-dreambooth`
- `sdxl-finetune`
- `sd3-lora`
- `flux-lora`
- `flux-finetune`

Count: `7`

### End-to-End Overlap
These types are visible in schema and also mapped by backend `/api/run`:
- `sd-lora`
- `sdxl-lora`
- `sd-dreambooth`
- `sdxl-finetune`
- `sd3-lora`
- `flux-lora`

Count: `6`

### Current Mismatch
- `lumina-lora`: has schema, but is not present in backend `trainer_mapping`; current `/api/run` path cannot launch it as-is.
- `flux-finetune`: is present in backend `trainer_mapping`, but no dedicated `mikazuki/schema/*.ts` training schema was found for it.

## Parameter Template Structure
The parameters do **not** belong to one single flat template.

Use this mental model instead:
- one shared parameter backbone in `mikazuki/schema/shared.ts`
- plus one model-specific schema per training family
- plus a few per-family field overrides

### Shared Backbone
The following blocks are reused repeatedly through `SHARED_SCHEMAS` or `UpdateSchema(...)`:
- dataset settings
- save settings
- LR and optimizer settings
- preview image settings
- log settings
- caption settings
- noise settings
- data enhancement
- other options
- precision / cache / batch options
- distributed training

### Model-Specific Layers
- `lora-master.ts`: shared backbone + SD/SDXL LoRA-specific fields
- `flux-lora.ts`: shared backbone + Flux-specific model files and options
- `sd3-lora.ts`: shared backbone + SD3-specific model files and options
- `lumina2-lora.ts`: shared backbone + Lumina2-specific model files and options
- `dreambooth.ts`: similar grouped form, but more self-contained than the LoRA family schemas
- `lora-basic.ts`: simplified training form, not the main expert schema

## Can Training Be Started By API
Yes, for the types that exist in backend `trainer_mapping`.

### Start Flow
`POST /api/run` does the following:
1. read JSON body
2. normalize parameter types
3. validate dataset and base model
4. save config into `config/autosave/<timestamp>.toml`
5. choose trainer script from `trainer_mapping`
6. call `process.run_train(...)`
7. create a background task and launch `accelerate`

### Return Shape
On success it returns a success response with a task id in the message text.

### Task Lifecycle API
- query tasks: `GET /api/tasks`
- terminate a task: `GET /api/tasks/terminate/{task_id}`

## Implementation Notes For Future Skill Work
- If future skill work wants “API-driven start training”, target `POST /api/run` first.
- Before adding `lumina-lora` support to the skill, patch backend `trainer_mapping` to include the Lumina trainer script.
- If future skill work wants “train by API without browser”, build request payloads from schema + preset instead of hardcoding all fields.
- Treat schema-visible support and backend-runnable support as two separate checks.
