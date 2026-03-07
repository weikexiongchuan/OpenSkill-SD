# HTTP Contract

## Endpoints
- start training: `POST /api/run`
- query tasks: `GET /api/tasks`
- terminate task: `GET /api/tasks/terminate/{task_id}`

## Input Rule
- `POST /api/run` expects a finalized JSON config payload.
- The payload must already include a valid `model_train_type` and the fields required by that training family.
- This skill does not decide all parameter values by itself.

## Minimal Execution Rule
- Prefer calling the bundled script instead of rewriting raw `curl` commands.
- Keep `base_url` user-supplied or inferred from the active lora-scripts deployment.

## Examples
Start training:
```bash
python l3/lora-scripts-api-training-task/scripts/lora_scripts_api_train.py start   --base-url http://127.0.0.1:28000   --config-file /path/to/train-config.json
```

Query tasks:
```bash
python l3/lora-scripts-api-training-task/scripts/lora_scripts_api_train.py tasks   --base-url http://127.0.0.1:28000
```

Terminate task:
```bash
python l3/lora-scripts-api-training-task/scripts/lora_scripts_api_train.py terminate   --base-url http://127.0.0.1:28000   --task-id <task-id>
```
