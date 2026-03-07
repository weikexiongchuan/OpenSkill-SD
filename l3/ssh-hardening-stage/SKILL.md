---
name: ssh-hardening-stage
description: Atomic capability skill for staged SSH daemon hardening after key-based login has already been verified. Use for dry-run preview or apply of remote sshd hardening, not for initial connection bootstrap.
---

# SSH Hardening Stage

## Purpose
Apply or preview a narrow, staged hardening change to `sshd` after access is safe.

## Capabilities
- Preview the remote hardening script in `dry-run` mode.
- Apply the hardening script with key-based SSH.
- Keep hardening separate from initial SSH connection bootstrap.

## Typical Inputs
- Host, port, user
- `dry-run` or `apply`
- Identity file

## Typical Outputs
- Hardening preview or applied result
- Restarted SSH service when `apply` is used

## Route
- Use this only after `l3/ssh-server-connect` has verified key login in a new terminal.

## Load On Demand
- `references/ssh-hardening-checklist.md`
