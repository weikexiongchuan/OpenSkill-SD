---
name: screen-session-manage
description: Atomic capability skill for managing long-running jobs in `screen`. Use for starting, stopping, listing, checking status, or attaching to a named `screen` session.
---

# Screen Session Manage

## Purpose
Provide one reusable interface for named `screen` session lifecycle actions.

## Capabilities
- Start a detached `screen` session with log capture.
- Check session status.
- Attach to a session.
- Stop a session.
- List active sessions.

## Typical Inputs
- Session name
- Log file path
- Command to run when starting

## Typical Outputs
- Running or stopped `screen` session
- Log file path

## Route
- Use this for any exact `screen` lifecycle task.

## Load On Demand
- `references/screen-operations.md`
