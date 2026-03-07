---
name: autodl-academic-model-download-acceleration
description: Capability skill for temporary AutoDL download acceleration using `/etc/network_turbo`, proxy environment checks, and mirror recipes. Use for precise tasks such as speeding up GitHub or HuggingFace downloads and disabling acceleration afterward.
---

# AutoDL Academic Model Download Acceleration

## Purpose
Provide reusable download-acceleration functions for AutoDL.

## Capabilities
- Check whether `/etc/network_turbo` is available.
- Inspect current proxy-related environment variables.
- Enable acceleration for the current shell or command.
- Provide mirror-oriented download recipes when direct access is slow.
- Disable acceleration after the download window closes.

## Typical Inputs
- Shell session or command to run
- Target repo, model, or dataset source
- Current server alias when local state tracking is needed

## Typical Outputs
- Accelerated download session
- Proxy diagnostics
- Cleaned-up environment after use

## Route
- Use this skill for exact “speed up downloads” actions.
- If slow downloads are discovered inside a larger deployment or training request, call this skill from the active `l2/` scenario.

## Load On Demand
- `references/academic-acceleration-policy.md`
- `references/terminal-notebook-usage.md`
- `references/download-recipes.md`
