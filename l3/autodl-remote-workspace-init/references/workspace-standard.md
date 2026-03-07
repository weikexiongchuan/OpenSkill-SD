# Workspace Standard

## Directory Layout
Use one canonical layout on every server. On AutoDL, prefer:
- `workspace-root=/root/autodl-tmp/workspace`
- upload staging at `/autodl-fs/data`

```text
<workspace-root>/
  current -> servers/<server-alias>
  shared/
    datasets/
    models/
    logs/
  servers/
    <server-alias>/
      repos/
      data/
      models/
      outputs/
      logs/
      runs/
      tmp/
      cache/
      env/
      comfyui/
      server.env
```

## AutoDL Data Placement
- Plan runtime work around `/root/autodl-tmp` first; current AutoDL rule-of-thumb is to prioritize the free `80G` class server-side runtime space for active projects.
- Treat `/autodl-fs/data` as the AutoDL “文件存储” mount; current rule-of-thumb is to plan around its free `20G` class shared quota first.
- Keep runtime-intensive data in `/root/autodl-tmp/workspace/servers/<alias>/...`.
- Keep raw uploads, long-lived base models, and cross-container shared datasets in `/autodl-fs/data/...`.
- Use symlink from workspace `data/` or `models/` to `/autodl-fs/data/<project>` when shared input is large; only copy into runtime paths when performance clearly benefits.

## Environment Rule
- Do not create project-local Python virtual environments on server.
- Use the container image system environment (typically `/root/miniconda3`) for reproducible replaceable-instance operations.

## Naming Rules
- Server alias: `provider-region-index`, example `autodl-westc-01`.
- Training run: `<date>-<project>-<model-family>-<seq>`.
- Screen session:
  - Training: `train-<run-name>`
  - Service: `svc-<service-name>-<alias>`

## Metadata Files
Maintain these files per server alias:
- Local markdown canonical:
  - `state.md`: server identity, login mode, runtime status.
  - `login/method.md`: login method details.
  - `services/comfyui.md`: service endpoint state.
  - `training/lora.md`: training status.
  - `timeline.md`: operation history.
- Remote optional mirror:
  - `server.env`: static server identity and storage notes on remote workspace.
- `runs/<run-name>/run.env`: training settings, base model, launch command, resume point.

If remote `server.env` is used, recommended fields:
```env
SERVER_ALIAS=<alias>
WORKSPACE_ROOT=<workspace-root>
SERVER_ROOT=<server-root>
LOGIN_METHOD=<key|password>
SSH_ALIAS=<optional-host-alias>
SSH_HOST=<host>
SSH_PORT=<port>
SSH_USER=<user>
```

Local markdown update command:
```bash
python scripts/record_server_state.py <workspace-root> <server-alias> <host> <port> <user> <key|password> <remote-workspace-root> [identity-file] [ssh-alias] [status]
```

## Retention Policy
- Keep all logs for active runs.
- Keep at least latest `N` checkpoints per run.
- Sync critical outputs to shared or external storage regularly.
