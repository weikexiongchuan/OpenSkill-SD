# OpenSkill-SD

一个面向 AutoDL、ComfyUI、SDXL / LoRA 工作流的三层 skill workspace。

## 你可以用它做什么
- 部署、启动、恢复 `ComfyUI`
- 部署、启动、管理 `lora-scripts` 训练界面与训练任务
- 连接和维护 AutoDL 远端服务器工作区
- 准备 LoRA 训练配置、底模、数据集与诊断材料
- 辅助 SDXL / LoRA base 选型

## 基础 CLI 引导
- `winget install -e --id OpenJS.NodeJS.LTS`：在 Windows 上安装 Node.js LTS，给后续 `npm`、Codex、Claude Code 和 Gemini CLI 提供运行环境。
- `npm install -g @openai/codex`：全局安装 OpenAI Codex CLI。这里我按官方写法修正了安装命令；`--dangerously-bypass-approvals-and-sandbox` 属于启动参数，不建议写在安装命令里。
- `codex --dangerously-bypass-approvals-and-sandbox`：启动 Codex，并跳过审批与沙箱限制；只适合你明确知道风险、且外部环境已经隔离的场景。日常使用直接运行 `codex` 即可。
- Claude 安装：`npm install -g @anthropic-ai/claude-code`
- Claude 启动：`claude`
- Gemini 安装：`npm install -g @google/gemini-cli`
- Gemini 启动：`gemini`

## 适合谁用
- 想把 AutoDL 上的 ComfyUI / LoRA 训练流程整理成可复用 skill 的人
- 想把“场景编排”和“原子能力”拆开维护的人
- 想让 agent 在低 token 成本下稳定命中正确技能入口的人

## 怎么开始
- 如果你的目标是一个完整场景，比如“部署 ComfyUI”或“恢复训练环境”，从 `docs/SKILL_INDEX.md` 开始。
- 如果你要找一个精确动作，比如“SSH 连接”、“状态记录”或“启动训练任务”，从 `docs/FUNCTION_INDEX.md` 开始。
- 进入对应条目后，再按需读取单个 `SKILL.md`、`references/` 或 `scripts/`。

## 推荐使用路径
1. 先在 `README.md` 了解仓库范围。
2. 宽泛目标走 `docs/SKILL_INDEX.md`。
3. 精确动作走 `docs/FUNCTION_INDEX.md`。
4. 命中后只进入一个目标 skill，再按需读取 `references/` 或执行 `scripts/`。

## 设计特点
- 低 token：优先走“入口索引 -> 单个 skill -> 按需 reference / script”的渐进式加载。
- 三层分工：`l1` 管知识与协议，`l2` 管场景编排，`l3` 管原子能力。
- 远端优先：默认面向 AutoDL 远端服务器实操，而不是只给步骤说明。

## 目录说明
- `l1/`：定义、协议、选型与诊断知识
- `l2/`：面向用户场景的编排 skill
- `l3/`：可直接执行的原子能力 skill
- `docs/`：用户导航索引

## 当前覆盖范围
- AutoDL 远端服务器接入、状态记录与远端工作区初始化
- ComfyUI 部署、启动、恢复、访问方式选择与常见排障
- `lora-scripts` 部署、启动、Web API 训练任务与状态记录
- LoRA 训练底模下载、数据集准备、样图提示词准备、配置定稿与训练诊断
- SDXL 生态底模对比与 LoRA base 选择建议
