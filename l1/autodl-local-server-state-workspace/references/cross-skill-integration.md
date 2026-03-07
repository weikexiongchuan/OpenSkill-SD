# Cross Skill Integration

## Pre-Read Rule
Before any server action, related skills should read:
1. `<workspace-root>/servers/<alias>/state.md`
2. `<workspace-root>/servers/<alias>/login/method.md`

## Post-Update Rule
After skill execution, related skills should update affected markdown files and append `timeline.md`.

## Completion Reminder (Required)
Use this reminder at the end of related skills:

```text
请更新本地服务器状态文件：
- state.md
- login/method.md（如登录方式有变化）
- services/comfyui.md、services/lora-scripts.md、storage/large-files.md、training/lora.md、training/models.md、training/datasets.md、training/configs.md、training/sample-prompts.md 或 training/analysis.md（按本次操作）
- timeline.md
```

## Skills that must reference this workspace
- `local-server-state-workspace-init`
- `local-server-state-record-update`
- `ssh-server-connect`
- `autodl-remote-workspace-init`
- `autodl-comfyui-deploy-screen`
- `autodl-lora-scripts-deploy-screen`
- `lora-training-state-record-update`
- `lora-training-config-import`
- `lora-training-config-prepare`
- `lora-training-dataset-prepare`
- `autodl-academic-model-download-acceleration` (optional endpoint context)
- `lora-basemodel-download` (planned/downloaded/manual-upload base model registration and large-file tracking)
- `lora-training-analysis`
- `lora-training-sample-prompts-prepare`
