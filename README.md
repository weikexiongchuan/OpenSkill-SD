# OpenSkill-SD

一个面向 AutoDL、ComfyUI、SDXL / LoRA 工作流的三层 skill workspace。

## 你可以用它做什么
- 部署、启动、恢复 `ComfyUI`
- 部署、启动、管理 `lora-scripts` 训练界面与训练任务
- 连接和维护 AutoDL 远端服务器工作区
- 准备 LoRA 训练配置、底模、数据集与诊断材料
- 辅助 SDXL / LoRA base 选型

## 怎么开始
- 如果你的目标是一个完整场景，比如“部署 ComfyUI”或“恢复训练环境”，从 `docs/SKILL_INDEX.md` 开始。
- 如果你要找一个精确动作，比如“SSH 连接”、“状态记录”或“启动训练任务”，从 `docs/FUNCTION_INDEX.md` 开始。
- 进入对应条目后，再按需读取单个 `SKILL.md`、`references/` 或 `scripts/`。

## 设计特点
- 低 token：优先走“入口索引 -> 单个 skill -> 按需 reference / script”的渐进式加载。
- 三层分工：`l1` 管知识与协议，`l2` 管场景编排，`l3` 管原子能力。
- 远端优先：默认面向 AutoDL 远端服务器实操，而不是只给步骤说明。

## 目录说明
- `l1/`：定义、协议、选型与诊断知识
- `l2/`：面向用户场景的编排 skill
- `l3/`：可直接执行的原子能力 skill
- `docs/`：用户导航索引
