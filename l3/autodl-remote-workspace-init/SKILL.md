---
name: autodl-remote-workspace-init
description: Atomic capability skill for initializing the standard remote AutoDL workspace layout and `server.env` file. Use for first-time remote workspace creation, not for local markdown state initialization.
---

# AutoDL Remote Workspace Init

## Purpose
Create the standard remote workspace directories for one server.

## Capabilities
- Create shared and per-server remote directories.
- Write `server.env` with workspace metadata.
- Refresh the `current` symlink.

## Typical Inputs
- Remote `<workspace-root>`
- `<server-alias>`

## Typical Outputs
- Standardized remote directory tree
- `server.env`
- Updated `current` symlink

## Route
- Use this when the remote workspace does not exist yet.
- Use `l3/local-server-state-record-update` separately if local markdown state also needs to be updated.

## Load On Demand
- `references/workspace-standard.md`
