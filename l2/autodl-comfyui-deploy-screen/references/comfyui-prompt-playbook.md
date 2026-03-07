# ComfyUI Prompt Playbook

## Usage Rule
Default to direct remote execution once the user provides usable server access.
Ask only for missing connection fields and the required access mode choice.
If the user does not request overrides, use these defaults:
- Deploy dir: `/root/autodl-tmp/comfyui/app`
- `screen` session: `comfyui-main`
- `public-port`: `6006` first, `6008` fallback
- `ssh-tunnel-cli` / `ssh-tunnel-gui`: `8188`

## Prompt Template: Access Mode Confirmation (Required)
```text
部署前只确认一个关键选择：访问模式三选一。默认部署目录是 `/root/autodl-tmp/comfyui/app`，默认会话名是 `comfyui-main`。\n
1) public-port：映射到 AutoDL 公网服务端口，默认 `6006`，不可用再试 `6008`\n
2) ssh-tunnel-cli（推荐）：服务跑在 `8188`，本地用 `ssh -L` 开隧道\n
3) ssh-tunnel-gui：服务跑在 `8188`，用官方客户端做端口代理\n
请直接回复其一；如果你直接回复“开始”，就按 `2) ssh-tunnel-cli（推荐）` 继续。\n
如果你还想改部署目录、会话名或端口，也一起说。\n
若账号不支持公网自定义服务（如未满足平台要求），自动切换到 `ssh-tunnel-cli` 或 `ssh-tunnel-gui`。
```

## Prompt Template: Precheck First
```text
请先执行 ComfyUI 预检，不要安装：
1) 检查 `/root/autodl-tmp/comfyui/app` 是否存在
2) 检查是否已有 `comfyui-main` 或相关 screen 会话在跑 ComfyUI
3) 按所选访问模式检查本地健康状态：`public-port` 检查 `6006` / `6008`，其余检查 `8188`
4) 输出结论：
   - A: 已在运行，可直接使用
   - B: 可直接启动（无需安装）
   - C: 需要安装依赖
   - D: 需要首次拉代码+安装
```

## Prompt Template: Asset Upload Reminder
```text
如果这次部署还缺模型或工作流素材，先只告诉用户要上传什么：
1) 上传位置：AutoDL 界面的“文件存储”标签
2) 服务器对应路径：`/autodl-fs/data`
3) 必需物按当前任务列出，例如 checkpoint / LoRA / VAE / workflow
4) 说明部署可以先继续；真正取模型时再按用户指定的那一份接到运行目录
```

## Prompt Template: Direct Start Path
```text
按“非首次安装”路径处理：
1) 不安装依赖
2) 按所选访问模式在 screen 启动 ComfyUI（`public-port` 默认 `6006` / `6008`，其余默认 `8188`）
3) 健康检查通过后回传访问与会话信息
4) 若启动失败，再给出失败原因并切换到安装路径
```

## Prompt Template: Install Path
```text
按“需要安装”路径处理：
1) 拉取或更新 ComfyUI 代码到 `/root/autodl-tmp/comfyui/app`
2) 使用系统环境安装依赖（禁止创建venv）
3) 在 screen 中按所选访问模式启动 main.py（`public-port` 默认 `6006` / `6008`，其余默认 `8188`）
4) 健康检查
5) 给出 AutoDL 端口映射操作提醒
```

## Prompt Template: Port Mapping Handoff
```text
部署完成后仅输出服务网址，不附带任何说明、API链接或其他URL。
```

## Output Format Suggestion
Return exactly one line:
`<service_url>`
