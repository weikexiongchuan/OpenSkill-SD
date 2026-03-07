---
name: proxy-env-manage
description: Atomic capability skill for creating or removing a `.proxy_env` file under a workspace root. Use for precise proxy environment setup before pull or install steps, not for network-turbo acceleration itself.
---

# Proxy Env Manage

## Purpose
Generate or remove a reusable proxy environment file for a workspace.

## Capabilities
- Write `.proxy_env` with proxy variables.
- Remove `.proxy_env` when proxy should be disabled.
- Keep proxy configuration separate from download acceleration.

## Typical Inputs
- `<workspace-root>`
- `<proxy-url>` or `none`

## Typical Outputs
- `.proxy_env` file or removal result

## Route
- Use this when a workspace needs proxy env setup.
- If the task is temporary AutoDL network turbo, use `l3/autodl-academic-model-download-acceleration` instead.

## Load On Demand
- `references/autodl-storage-and-proxy.md`
