# Skill Index

按层检索 skill，先看这里，再打开单个 `SKILL.md`。

## Layer Roles
- `l1`：定义、协议、状态结构；用于澄清规则，不直接承担远端执行。
- `l2`：场景编排；用于判断当前属于首次部署、续启动、恢复还是升级，并组织后续 `l3`。
- `l3`：原子能力；用于执行单个脚本、命令或状态更新动作。

## Progressive Loading
- 宽泛目标：先看本文件，再只打开一个匹配的 `l2/*/SKILL.md`。
- 精确功能：改看 `docs/FUNCTION_INDEX.md`，再只打开一个匹配的 `l3/*/SKILL.md`。
- 只有在当前 skill 明确需要时，才继续读对应 `references/` 或执行 `scripts/`。
- 不要一次性展开多个 `AGENTS.md`、多个 `SKILL.md` 或整包 `references/`。

## User-Facing Scope
- 当前可直接代办的用户场景由 `l2/references/scene-registry.yaml` 统一维护。
- 用户级回答优先说“能得到什么服务”，不要先展开隧道、端口或内部术语。
- 具体的能力聚合、回复模板和接入分流，统一由 `l2` 场景层负责。

## Service-Task First Check
- 涉及 `AutoDL` 服务器实操时，先检查当前 local workspace。
- 优先读取 `<workspace-root>/servers/<alias>/state.md` 与 `login/method.md`，用来支持后续 `l2` 场景判断首次接入、续启动、恢复还是升级。

| skill | layer | use when | related |
|---|---|---|---|
| `autodl-local-server-state-workspace` | `l1` | 需要本地状态 workspace 结构、状态文件规则、跨 skill 更新规则 | `l2/*`, `l3/*` |
| `sdxl-ecosystem-base-selection` | `l1` | 需要比较 SDXL 家族、选 LoRA base、确认兼容性或许可风险 | - |
| `lora-scripts-training-schema-structure` | `l1` | 需要理解 lora-scripts Web 训练 schema 结构、共享模板与家族差异 | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-scripts-api-training-task` |
| `lora-scripts-beginner-parameter-playbook` | `l1` | 需要小白版 lora-scripts 参数字典、按模型起手值、按画风/角色/服装配饰场景给参数建议，或读取内置训练模板 | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-scripts-api-training-task` |
| `lora-training-diagnosis-playbook` | `l1` | 需要基于官方资料判断 LoRA 训练为什么失败、为什么没学住、为什么 TensorBoard 没信号，或区分已确认问题与推断风险 | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-training-analysis` |
| `autodl-comfyui-deploy-screen` | `l2` | 用户目标是部署、启动、暴露、恢复 ComfyUI | `l3/ssh-server-connect`, `l3/local-server-state-record-update`, `l3/screen-session-manage` |
| `autodl-lora-scripts-deploy-screen` | `l2` | 用户目标是部署、启动、暴露、恢复 Akegarasu `lora-scripts` 训练 GUI，或判断其 Web 训练能力 | `l1/lora-scripts-training-schema-structure`, `l1/lora-scripts-beginner-parameter-playbook`, `l1/lora-training-diagnosis-playbook`, `l3/lora-basemodel-download`, `l3/lora-training-dataset-prepare`, `l3/lora-training-sample-prompts-prepare`, `l3/lora-training-analysis`, `l3/lora-scripts-api-training-task`, `l3/lora-training-state-record-update`, `l3/ssh-server-connect`, `l3/local-server-state-record-update`, `l3/screen-session-manage` |
| `ssh-server-connect` | `l3` | 需要建立 SSH 连通性、补公钥、密码回退执行、验证 key 登录 | `l1/autodl-local-server-state-workspace` |
| `ssh-hardening-stage` | `l3` | 需要在 key 登录验证后做 staged SSH hardening | `l3/ssh-server-connect` |
| `local-server-state-workspace-init` | `l3` | 需要创建本地 server-state workspace 骨架和默认 markdown 文件 | `l1/autodl-local-server-state-workspace` |
| `local-server-state-record-update` | `l3` | 需要更新 `state.md`、`login/method.md`、`timeline.md` | `l1/autodl-local-server-state-workspace` |
| `autodl-remote-workspace-init` | `l3` | 需要初始化远端标准工作目录和 `server.env` | `l1/autodl-local-server-state-workspace` |
| `autodl-host-facts-collect` | `l3` | 需要收集 GPU、磁盘、挂载和 `screen` 现状 | `l3/autodl-remote-workspace-init` |
| `screen-session-manage` | `l3` | 需要启动、停止、查看、附着 `screen` 会话 | `l2/*` |
| `proxy-env-manage` | `l3` | 需要生成或移除 `.proxy_env` 代理环境文件 | `l3/autodl-remote-workspace-init` |
| `autodl-academic-model-download-acceleration` | `l3` | 需要临时加速 GitHub/HuggingFace 下载并在结束后恢复环境 | `l2/*` |
| `lora-basemodel-download` | `l3` | 需要选择 LoRA 训练底模版本槽位、生成 HF 镜像下载命令，或把底模下载记录写回对应服务器 workspace | `l2/autodl-lora-scripts-deploy-screen`, `l3/ssh-server-connect`, `l3/autodl-academic-model-download-acceleration`, `l3/lora-training-config-prepare` |
| `lora-training-dataset-prepare` | `l3` | 需要把本地训练集上传到当前服务器，检查图片与同名 txt 是否成对，并在服务器上按 64 倍数裁剪或补白 | `l2/autodl-lora-scripts-deploy-screen`, `l3/ssh-server-connect`, `l3/lora-training-config-prepare` |
| `lora-training-sample-prompts-prepare` | `l3` | 需要为 LoRA 训练准备样图提示词，支持随机抽取 3 条标注或使用用户自定义提示词，并登记到当前服务器 workspace | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-training-config-prepare`, `l3/ssh-server-connect` |
| `lora-training-analysis` | `l3` | 需要分析当前服务器上的 LoRA 训练数据、配置、日志、API 状态与 TensorBoard 事件文件，并把诊断写回 workspace | `l1/lora-training-diagnosis-playbook`, `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-training-dataset-prepare`, `l3/lora-training-config-prepare` |
| `lora-scripts-api-training-task` | `l3` | 需要通过 lora-scripts Web API 启动、查询或终止训练任务 | `l1/lora-scripts-training-schema-structure`, `l1/lora-scripts-beginner-parameter-playbook`, `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-training-state-record-update` |
| `lora-training-state-record-update` | `l3` | 需要把 LoRA 训练模板选择、任务状态和运行记录动态写回对应服务器 workspace | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-scripts-api-training-task` |
| `lora-training-config-import` | `l3` | 需要把用户自定义训练配置导入对应服务器 workspace，并明确标记为 `manual-import` | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-scripts-api-training-task` |
| `lora-training-config-prepare` | `l3` | 需要把训练配置绑定到当前服务器的 base model、数据集目录和输出名，并生成可执行 JSON | `l2/autodl-lora-scripts-deploy-screen`, `l3/lora-scripts-api-training-task` |
