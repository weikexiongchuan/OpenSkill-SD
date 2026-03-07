---
name: local-server-state-record-update
description: Atomic capability skill for updating local markdown records inside the canonical server-state workspace. Use for writing `state.md`, `login/method.md`, and `timeline.md` after server bootstrap or login-mode changes.
---

# Local Server State Record Update

## Purpose
Update the persistent local markdown records for one server.

## Capabilities
- Write `state.md` after server bootstrap or verification.
- Write `login/method.md` after login-mode changes.
- Append `timeline.md` entries during those updates.

## Typical Inputs
- `<workspace-root>` and `<server-alias>`
- Host, port, user
- Login mode and optional identity file
- Optional SSH alias and remote workspace root

## Typical Outputs
- Updated markdown records in the local workspace

## Route
- Use this skill when the local state must change.
- Use `l3/local-server-state-workspace-init` first if the workspace skeleton does not exist yet.
