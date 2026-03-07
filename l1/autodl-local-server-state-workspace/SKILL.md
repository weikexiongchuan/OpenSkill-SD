---
name: autodl-local-server-state-workspace
description: Canonical schema for the local markdown workspace that stores AutoDL server state. Use when you need folder layout, state-file conventions, or cross-skill update rules for per-server login, service, and timeline records. Not for remote execution.
---

# AutoDL Local Server State Workspace

## Purpose
Define the single local source of truth for AutoDL server state.

## Defines
- Workspace folder layout under `<workspace-root>/servers/<alias>/`.
- Required markdown state files and update points.
- Cross-skill rules for reading and writing state.
- Safe handling of login method metadata without storing plaintext passwords.

## Typical Inputs
- `<workspace-root>`
- `<server-alias>`
- Login mode, service URL, run status, timeline updates

## Typical Outputs
- `state.md`
- `login/method.md`
- `timeline.md`
- Other per-server markdown records defined by the references

## Route
- Read this skill before any skill that needs persistent server context.
- If the user asks to create the local workspace skeleton, use `l3/local-server-state-workspace-init`.
- If the user asks to update server or login markdown state, use `l3/local-server-state-record-update`.
- If the user asks for execution on a server, switch to an `l2/` scenario or an `l3/` capability after confirming the workspace schema.

## Load On Demand
- `references/workspace-layout.md`
- `references/state-files.md`
- `references/cross-skill-integration.md`
