# AutoDL Storage and Proxy

## Storage Discovery First
Do not assume mount points. Detect actual layout on each instance.

Run:
```bash
lsblk -f
df -hT
mount | sort
```

Also run:
```bash
nvidia-smi
```

## Common AutoDL Pattern
Typical instances expose:
- System disk for OS and base runtime (often small, such as 20G class).
- Container runtime work disk mounted at `/root/autodl-tmp` (current AutoDL planning rule: treat the free server-side runtime space as `80G` class first).
- AutoDL UI label “文件存储” maps to `/autodl-fs/data`; current planning rule: treat its free shared quota as `20G` class first, and avoid unnecessary duplicate large files because extra usage may be billed.

Use this rule:
1. Put active project code, environments, checkpoints in use, and running outputs under `/root/autodl-tmp`.
2. Treat `/autodl-fs/data` as shared persistence and staging storage for user uploads, long-lived base models, and shared datasets.
3. Copy or symlink staged data from `/autodl-fs/data` into `/root/autodl-tmp` only when runtime performance or tool compatibility makes it necessary.

Because mount sizes can differ by image and package, always trust live detection output over fixed size assumptions.

## Workspace Root Recommendation
Default to `/root/autodl-tmp/workspace`, then keep all project artifacts under:
- `<workspace-root>/servers/<server-alias>/repos`
- `<workspace-root>/servers/<server-alias>/data`
- `<workspace-root>/servers/<server-alias>/models`
- `<workspace-root>/servers/<server-alias>/outputs`
- `<workspace-root>/servers/<server-alias>/runs`
- `<workspace-root>/servers/<server-alias>/logs`

## Proxy for Model and Dependency Pulls
When official AutoDL proxy is available, configure shell exports:
```bash
export http_proxy="<proxy-url>"
export https_proxy="<proxy-url>"
export all_proxy="<proxy-url>"
```

Set `no_proxy` for local traffic:
```bash
export no_proxy="localhost,127.0.0.1,::1"
```

Persist with `scripts/configure_proxy_env.sh` and source it before `git clone`, `pip install`, and model downloads.

## Validation Checklist
1. Run `curl -I https://huggingface.co` with proxy loaded.
2. Run `git ls-remote <repo-url>` with proxy loaded.
3. Run a small `pip download` check if Python packages are required.
4. Run `df -hT /root/autodl-tmp /autodl-fs/data` and record capacities in local markdown `state.md`.
