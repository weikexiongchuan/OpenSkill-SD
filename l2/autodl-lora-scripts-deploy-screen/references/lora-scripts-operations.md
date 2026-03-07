# LoRA Scripts Operations

## Install Layout
Recommended structure under `/root/autodl-tmp/lora-scripts`:
- `app` for repository
- `data` for datasets or symlink targets
- `output` for training outputs

## Storage Budget
- AutoDL 运行盘默认按 `/root/autodl-tmp` 的 `80G` 免费空间规划。
- AutoDL 界面“文件存储”对应 `/autodl-fs/data`，默认按 `20G` 免费空间规划；超额部分可能计费。
- 因此不要默认把整套底模、数据集和输出在 `tmp` 与 `fs` 双份长期保留。

## Default Parameters
- Server root: `/root/autodl-tmp`
- Install dir: `/root/autodl-tmp/lora-scripts/app`
- `screen` session: `lora-scripts-main`
- `ssh-tunnel-cli` / `ssh-tunnel-gui` GUI port: `28000`
- default tensorboard port: `6016`
- `public-port` preferred AutoDL service port: `6006` (fallback `6008`)

## Upstream Assumptions
- Official upstream repo: `https://github.com/Akegarasu/lora-scripts`
- Official Linux install entry: `install.bash --disable-venv`
- Official GUI entry: `python gui.py --listen --port <port>`
- Upstream default GUI port is `28000`; upstream default tensorboard port is `6006`

## Execution Style
- Once usable SSH access is available, execute the deployment flow directly instead of only returning a checklist.
- Ask only for required choices that cannot be inferred. For access choice, use plain Chinese descriptions for the user and keep the raw mode names internal.
- Keep user-facing prompts brief: prefer `1` sentence, and only use `2` sentences when the difference between options must be clarified.

## Environment Policy
- Do not create or use project-local virtual environments (`venv`, `.venv`) on AutoDL.
- Use the system/container Python environment (usually Miniconda in image) so runtime matches the container lifecycle model.
- Use the upstream installer in no-venv mode after exporting the desired interpreter path.
- Start the GUI with `--skip-prepare-environment` after installation to avoid repeated environment bootstrap.

## Basic Deploy Flow
1. Confirm the user-facing access choice before execution, explain the difference in Chinese, then map it internally to `public-port`, `ssh-tunnel-cli`, or `ssh-tunnel-gui`.
2. Run precheck to determine whether install is needed.
3. If precheck passes, start lora-scripts directly in `screen`.
4. If precheck fails, pull/update repository and install dependencies.
5. Start service and run health check on the chosen GUI port.
6. Apply selected access mode commands.
7. Once the final URL is reachable, open it in the local browser by default and keep the user-facing reply minimal.

Example:
```bash
scripts/install_lora_scripts.sh /root/autodl-tmp/lora-scripts/app
LORA_SCRIPTS_PORT=<6006|6008|28000> LORA_SCRIPTS_TENSORBOARD_PORT=6016 scripts/lora_scripts_screen_ctl.sh start /root/autodl-tmp/lora-scripts/app lora-scripts-main
scripts/lora_scripts_healthcheck.sh 127.0.0.1 <6006|6008|28000>
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
Run the GUI on an AutoDL service port and proxy tensorboard internally on `6016`.

Example:
```bash
LORA_SCRIPTS_PORT=6006 LORA_SCRIPTS_TENSORBOARD_PORT=6016 scripts/lora_scripts_screen_ctl.sh start /root/autodl-tmp/lora-scripts/app lora-scripts-main
```

### ssh-tunnel-cli
Keep the GUI on internal port `28000` and tunnel from local machine:
```bash
ssh -CN -L 28000:127.0.0.1:28000 -p <ssh-port> <user>@<host>
```

If only password login is available, start the local tunnel in background instead of asking the user to keep a terminal open:
```bash
SSH_PASSWORD=<password> l3/ssh-server-connect/scripts/ssh_password_tunnel_bg.sh <host> <ssh-port> <user> 28000 127.0.0.1 28000
```

When usable SSH credentials are already available, prefer creating this tunnel automatically during deployment and return the final local URL plus the fixed short support sentence.

### ssh-tunnel-gui
Use AutoDL official client/proxy tool to forward internal port `28000` to local environment.

## Browser Open Step
When the final URL is ready, open it automatically on the local machine by default instead of asking the user to copy it manually.
- The final user-facing reply should default to the URL plus the fixed short support sentence `如果服务不可用请告诉我，我将为您排查问题。`.
- If browser open fails, use one short fallback sentence instead of a multi-line explanation.

Example:
```bash
scripts/open_browser_url.sh <final-url>
```

## Markdown State Maintenance
After deployment/update, write local server state markdown and record the actual GUI port chosen:

```bash
python scripts/record_lora_scripts_state.py <workspace-root> <server-alias> <session> <service-port> <tensorboard-port> <public-port|ssh-tunnel-cli|ssh-tunnel-gui> <service-url> <ok|failed|unknown>
```

## Training Note
- When the user broadly asks to train, default to offering built-in templates first instead of opening with custom parameter explanation.
- If the user has not yet said whether this is `角色`、`画风` or `服装配饰`, ask that first; this is a blocking choice before template selection and execution.
- Keep the first offer user-facing and short, but list all currently available templates in the current scope instead of only a subset.
- Mark the default path as `（推荐）`; if the user only replies `开始`、`按默认` or `用推荐的`, continue with the current recommended template.
- If the user needs custom values, only then mention that built-in parameter guidance is available.
- Actual training run state should be written back into local `training/lora.md` for the current server.
- If the user brings a custom config file, import it into `training/imported-configs/` first and register it in `training/configs.md` as `manual-import`.
- Before API execution, prepare one runnable config by binding the current server's base model path, checked dataset directory, and `output_name`; store that result under `training/prepared-configs/`.
- If the platform supports sample images, treat them as default-on in this workflow: confirm the prompt source first, default to random 3 captions from the current dataset, and carry the prepared prompt file into the final config.
- If the user chooses manual prompts, accept 1 to 3 prompt lines; otherwise use the default random 3-caption branch.
- Dataset check is mandatory before training: images should have same-name `.txt` captions, and width and height should both be multiples of `64`.
- Default image fix policy is centered crop on the server; optional policy is upward white padding; if the user only wants a report, use check-only.
- Prepared config must normalize numeric-looking strings before API start: for example `1e-4` should become a numeric learning rate, and a range like `8~10` should default to its left-side starter value `8`.
- For `sdxl-lora` and sibling SDXL runs, add one startup supplement before the first actual run: prefetch the required tokenizer repos on the remote side, then start training.
- Training is only counted as truly started after two checks both pass: task status is still `RUNNING`, and a new TensorBoard event file appears under the configured logging directory.
- If the task is only `RUNNING` but TensorBoard still has no event file, keep monitoring instead of telling the user it already started successfully.

## Asset Delivery Flow
- 如果当前部署或训练缺 base model、dataset 或 custom config，先告诉用户上传到 AutoDL 界面的“文件存储”标签。
- 用户上传后，默认从 `/autodl-fs/data/...` 取用；只有当前训练明确需要更高吞吐时，才复制到 `/root/autodl-tmp/...`。
- 服务部署完成后，等用户明确说用哪个模型或哪份数据，再继续取用。
- 如果用户的数据集在本地电脑，也可以直接走 `l3/lora-training-dataset-prepare`：先上传到服务器，再在服务器上检查图片+txt 配对和 64 倍数尺寸。
- 若用户不想手动上传，说明后续也可以走下载脚本分支，并切到 `l3/lora-basemodel-download` 解析底模槽位、镜像下载命令、进度监控与登记记录。
- 若远端下载偏慢，也可以改走“本地先下载，再上传到文件存储”的分支；上传后即可直接取用。
