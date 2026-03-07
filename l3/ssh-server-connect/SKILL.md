---
name: ssh-server-connect
description: Atomic capability skill for establishing SSH connectivity to a server. Use for creating a local key pair, installing a public key with password fallback, running one-off password-mode SSH or SCP, and verifying key-based login. Not for SSH daemon hardening.
---

# SSH Server Connect

## Purpose
Provide the minimum reusable actions needed to connect to a remote server over SSH.

## Capabilities
- Ensure a local SSH key exists.
- Install a public key on the remote host when password access is available.
- Run one-off SSH and SCP commands in password mode when key login is not ready.
- Start a local SSH tunnel in background when only password login is available.
- Verify key-based login.

## Typical Inputs
- Host, port, and user
- Identity file or public key path
- Optional `SSH_PASSWORD`

## Typical Outputs
- Local key pair
- Remote authorized key installed
- Verified key login
- One-off password-mode command or copy result
- Background tunnel PID/log files and a ready local forwarded port

## Route
- Use this skill when the task is “connect to the server” or “make SSH usable”.
- If the task is to update local markdown records, switch to `l3/local-server-state-record-update`.
- If the task is to harden `sshd`, switch to `l3/ssh-hardening-stage` after key login is verified.

## Load On Demand
- `references/ssh-key-login-workflow.md`
