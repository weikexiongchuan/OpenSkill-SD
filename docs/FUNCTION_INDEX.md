# Function Index

按功能检索，命中后再打开对应 skill。

- 命中后只打开一个目标 `l3/*/SKILL.md`，不要继续扫同层其他 skill。
- 相关 `references/` 与 `scripts/` 只在当前 skill 明确需要时再加载或执行。

| function | skill |
|---|---|
| 定义本地 server state workspace 目录结构 | `l1/autodl-local-server-state-workspace` |
| 定义 `state.md` / `login/method.md` / `timeline.md` 更新规则 | `l1/autodl-local-server-state-workspace` |
| 比较 SDXL Base / Illustrious / NoobAI / Animagine / Pony | `l1/sdxl-ecosystem-base-selection` |
| 选择 LoRA 训练 base model | `l1/sdxl-ecosystem-base-selection` |
| 部署、启动或恢复 ComfyUI 场景 | `l2/autodl-comfyui-deploy-screen` |
| 选择 ComfyUI 访问方式（直接给网址 / 只在本机打开 / AutoDL 客户端转发） | `l2/autodl-comfyui-deploy-screen` |
| 部署、启动或恢复 lora-scripts 场景 | `l2/autodl-lora-scripts-deploy-screen` |
| 判断 lora-scripts Web 平台支持哪些训练家族 | `l2/autodl-lora-scripts-deploy-screen` |
| 选择 lora-scripts 访问方式（直接给网址 / 只在本机打开 / AutoDL 客户端转发） | `l2/autodl-lora-scripts-deploy-screen` |
| 理解 lora-scripts Web 训练参数模板结构 | `l1/lora-scripts-training-schema-structure` |
| 获取 lora-scripts 小白参数字典 | `l1/lora-scripts-beginner-parameter-playbook` |
| 按模型给 lora-scripts 起手参数 | `l1/lora-scripts-beginner-parameter-playbook` |
| 按二次元 / 三次元给 lora-scripts 起手参数 | `l1/lora-scripts-beginner-parameter-playbook` |
| 按画风 / 角色 / 服装配饰给 LoRA 参数建议 | `l1/lora-scripts-beginner-parameter-playbook` |
| 提供 LoRA 训练模板选项 | `l1/lora-scripts-beginner-parameter-playbook` |
| 解释为什么 LoRA 训练失败或没学住 | `l1/lora-training-diagnosis-playbook` |
| 区分 LoRA 训练里的已确认问题与推断风险 | `l1/lora-training-diagnosis-playbook` |
| 分析二次元 / 三次元数据与 caption 是否错配 | `l1/lora-training-diagnosis-playbook` |
| 初始化本地 server-state workspace 骨架 | `l3/local-server-state-workspace-init` |
| 更新 `state.md` / `login/method.md` / `timeline.md` | `l3/local-server-state-record-update` |
| 创建本地 SSH key | `l3/ssh-server-connect` |
| 用密码模式执行 SSH / SCP 回退 | `l3/ssh-server-connect` |
| 用密码模式后台挂起本地 SSH tunnel | `l3/ssh-server-connect` |
| 安装公钥并验证 key 登录 | `l3/ssh-server-connect` |
| 以 dry-run / apply 方式做 SSH hardening | `l3/ssh-hardening-stage` |
| 初始化标准远端 workspace 目录 | `l3/autodl-remote-workspace-init` |
| 收集 GPU / 磁盘 / 挂载 / screen 信息 | `l3/autodl-host-facts-collect` |
| 管理 screen 长任务会话 | `l3/screen-session-manage` |
| 生成或移除 `.proxy_env` | `l3/proxy-env-manage` |
| 检查 `/etc/network_turbo` 可用性 | `l3/autodl-academic-model-download-acceleration` |
| 临时开启或关闭下载加速 | `l3/autodl-academic-model-download-acceleration` |
| GitHub / HuggingFace 下载镜像策略 | `l3/autodl-academic-model-download-acceleration` |
| 选择 LoRA 训练底模版本槽位 | `l3/lora-basemodel-download` |
| 生成 LoRA 底模 HF 镜像下载命令 | `l3/lora-basemodel-download` |
| 记录底模下载或手动上传状态 | `l3/lora-basemodel-download` |
| 在远端服务器下载 LoRA 底模并汇报进度 | `l3/lora-basemodel-download` |
| 记录服务器大文件路径台账 | `l3/lora-basemodel-download` |
| 把本地训练集上传到当前服务器 | `l3/lora-training-dataset-prepare` |
| 检查训练集图片与同名 txt 是否成对 | `l3/lora-training-dataset-prepare` |
| 检查训练集图片尺寸是否为 64 的倍数 | `l3/lora-training-dataset-prepare` |
| 在服务器上按中心裁剪训练集图片 | `l3/lora-training-dataset-prepare` |
| 在服务器上给训练集图片补白到 64 倍数 | `l3/lora-training-dataset-prepare` |
| 记录训练集检查结果和远端路径 | `l3/lora-training-dataset-prepare` |
| 为 LoRA 训练准备样图提示词 | `l3/lora-training-sample-prompts-prepare` |
| 随机抽取 3 条标注做训练样图 | `l3/lora-training-sample-prompts-prepare` |
| 记录样图提示词方案 | `l3/lora-training-sample-prompts-prepare` |
| 分析 LoRA 训练数据质量 | `l3/lora-training-analysis` |
| 分析 LoRA 训练过程、日志和 TensorBoard 信号 | `l3/lora-training-analysis` |
| 把 LoRA 训练诊断写回 `training/analysis.md` | `l3/lora-training-analysis` |
| 通过 lora-scripts Web API 启动训练任务 | `l3/lora-scripts-api-training-task` |
| 查询 lora-scripts Web API 训练任务 | `l3/lora-scripts-api-training-task` |
| 终止 lora-scripts Web API 训练任务 | `l3/lora-scripts-api-training-task` |
| 把 LoRA 训练状态写回对应服务器 workspace | `l3/lora-training-state-record-update` |
| 导入用户自定义 LoRA 训练配置 | `l3/lora-training-config-import` |
| 把导入配置注册到对应服务器 workspace | `l3/lora-training-config-import` |
| 绑定训练配置的 base model 和数据集目录 | `l3/lora-training-config-prepare` |
| 把训练配置定稿成可执行 JSON | `l3/lora-training-config-prepare` |
