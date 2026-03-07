# ComfyUI Operations

## Install Layout
Recommended structure under `/root/autodl-tmp/comfyui`:
- `app` for repository
- `models` for shared model storage
- `custom_nodes` for optional custom nodes

## Storage Budget
- AutoDL 运行盘默认按 `/root/autodl-tmp` 的 `80G` 免费空间规划。
- AutoDL 界面“文件存储”对应 `/autodl-fs/data`，默认按 `20G` 免费空间规划；超额部分可能计费。
- 因此不要默认把整套模型长期在 `tmp` 和 `fs` 双份保留。

## Default Parameters
- Server root: `/root/autodl-tmp`
- Install dir: `/root/autodl-tmp/comfyui/app`
- `screen` session: `comfyui-main`
- `ssh-tunnel-cli` / `ssh-tunnel-gui` service port: `8188`
- `public-port` preferred AutoDL service port: `6006` (fallback `6008`)

## Execution Style
- Once usable SSH access is available, execute the deployment flow directly instead of only returning a checklist.
- Ask only for required choices that cannot be inferred. For access choice, use plain Chinese descriptions for the user and keep the raw mode names internal.
- Keep user-facing prompts brief: prefer `1` sentence, and only use `2` sentences when the difference between options must be clarified.

## Environment Policy
- Do not create or use project-local virtual environments (`venv`, `.venv`) on AutoDL.
- Use the system/container Python environment (usually Miniconda in image) so runtime matches the container lifecycle model.
- If multiple Python binaries exist, prefer `/root/miniconda3/bin/python` unless a different system interpreter is explicitly required.

## Basic Deploy Flow
1. Confirm the user-facing access choice before execution, explain the difference in Chinese, then map it internally to `public-port`, `ssh-tunnel-cli`, or `ssh-tunnel-gui`.
2. Run precheck to determine whether install is needed.
3. If precheck passes, start ComfyUI directly in `screen`.
4. If precheck fails, pull/update repository and install dependencies.
5. Start service and run health check on the chosen service port.
6. Apply selected access mode commands.
7. Once the final URL is reachable, open it in the local browser by default and keep the user-facing reply minimal.

Example:
```bash
scripts/install_comfyui.sh /root/autodl-tmp/comfyui/app
COMFYUI_PORT=<6006|6008|8188> scripts/comfyui_screen_ctl.sh start /root/autodl-tmp/comfyui/app comfyui-main
scripts/comfyui_healthcheck.sh 127.0.0.1 <6006|6008|8188>
```

## Precheck Decision
Use this branch order before installation:
1. If `screen` session already running and healthcheck is ok: keep running, skip install.
2. If app directory exists but not running: try direct start first.
3. If start fails because modules/deps are missing: run install then retry start.
4. If app directory missing: clone + install + start.
5. If `screen` is running but healthcheck fails, wait and recheck once before escalation.

## Access Mode Commands
### public-port
Run ComfyUI on an AutoDL service port and use the AutoDL public URL. Prefer `6006`; if unavailable, use `6008`.

Example:
```bash
COMFYUI_PORT=6006 scripts/comfyui_screen_ctl.sh start /root/autodl-tmp/comfyui/app comfyui-main
```

### ssh-tunnel-cli
Keep ComfyUI on internal port `8188` and tunnel from local machine:
```bash
ssh -CN -L 8188:127.0.0.1:8188 -p <ssh-port> <user>@<host>
```

If only password login is available, start the local tunnel in background instead of asking the user to keep a terminal open:
```bash
SSH_PASSWORD=<password> l3/ssh-server-connect/scripts/ssh_password_tunnel_bg.sh <host> <ssh-port> <user> 8188 127.0.0.1 8188
```

When usable SSH credentials are already available, prefer creating this tunnel automatically during deployment and return the final local URL plus the fixed short support sentence.

## Browser Open Step
When the final URL is ready, open it automatically on the local machine by default instead of asking the user to copy it manually.
- The final user-facing reply should default to the URL plus the fixed short support sentence `如果服务不可用请告诉我，我将为您排查问题。`.
- If browser open fails, use one short fallback sentence instead of a multi-line explanation.

Example:
```bash
scripts/open_browser_url.sh <final-url>
```

### ssh-tunnel-gui
Use AutoDL official client/proxy tool to forward internal port `8188` to local environment.

## Markdown State Maintenance
After deployment/update, write local server state markdown and record the actual service port chosen:

```bash
python scripts/record_comfyui_state.py <workspace-root> <server-alias> <session> <service-port> <public-port|ssh-tunnel-cli|ssh-tunnel-gui> <service-url> <ok|failed|unknown>
```

## Model Management
- Store checkpoints and LoRA files in a persistent workspace path.
- Use symlink or ComfyUI extra model path config to avoid duplicated copies.
- Version model sets with dated snapshots if reproducibility matters.

## Upgrade Strategy
1. Stop screen session.
2. Pull latest repository changes.
3. Reinstall requirements in system environment if changed.
4. Start new session and run health check.

## Asset Delivery Flow
- 如果当前部署缺 checkpoint、LoRA、VAE 或 workflow，先告诉用户上传到 AutoDL 界面的“文件存储”标签。
- 服务部署完成后，再按用户明确要用的那一份素材，从 `/autodl-fs/data/...` 接到运行目录。
- 需要性能时复制到 `/root/autodl-tmp/comfyui/models/...`；不需要时优先软链或额外模型路径配置。
- 若用户不想手动上传，说明后续也可以走下载脚本分支。
