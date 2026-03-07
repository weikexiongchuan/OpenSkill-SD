# AGENTS

## Goal
维护一个低 token 的三层 skill workspace，服务 AutoDL、ComfyUI 和 SDXL/LoRA base 选型任务。

## Entry Rules
1. 宽泛目标先读 `docs/SKILL_INDEX.md`，精确功能先读 `docs/FUNCTION_INDEX.md`。
2. 用户目标是宽泛场景时，先进 `l2/`。
3. 用户目标是精确功能或命令时，先进 `l3/`。
4. 术语、状态结构、模型选择不清楚时，再补读 `l1/`。
5. 涉及 `AutoDL` 远端实操时，第一步先检查当前 local server-state workspace；优先读取现有 `state.md` 与 `login/method.md`，先判定是首次接入、首次部署、续启动、恢复还是升级。
6. 默认不要同时加载多个 skill body；优先“索引 -> 单个 skill -> 按需 references/scripts”，不要一次性展开多个 `AGENTS.md`、多个 `SKILL.md` 或整包 `references/`。

## Default Operating Assumptions
- 未特别说明时，把服务类任务视为 `AutoDL` 远端服务器实操，而不是纯步骤讲解。
- 一旦用户提供可用 SSH 信息，优先直接连机执行；只对必须确认的选项提问。
- `ComfyUI` 默认部署目录写死为 `/root/autodl-tmp/comfyui/app`，默认用 `screen` 托管。
- `ComfyUI` 暴露方式不能擅自假定；必须先让用户在 `public-port`、`ssh-tunnel-cli`、`ssh-tunnel-gui` 中选择。
- 若用户选 `public-port`，默认优先 `6006`，不可用再回退 `6008`；若走 SSH/GUI 隧道，默认服务端口 `8188`。

## Layer Meanings
- `l1`：定义、协议、结构、选型知识。
- `l2`：面向用户目标的场景 skill，负责组织多个能力。
- `l3`：可直接执行的能力 skill，负责函数、脚本、命令。

## Authoring Rules
- 一个 skill 只保留一个主职责。
- `SKILL.md` 只写概要、入口、输入输出、关联 skill。
- 细节放 `references/` 或 `scripts/`，按需读取。
- 索引与 `AGENTS.md` 必须写清分层职责，以及“索引 -> 单 skill -> 按需 references/scripts”的渐进式暴露规则。
- 本仓库不设 `l4`。
