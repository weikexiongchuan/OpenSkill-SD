# Field Validated Notes

## Validation Context
These notes come from real execution on an AutoDL test server in `west-C`.

## Verified Storage Facts
- `/` is container overlay filesystem and should not be used as main project workspace.
- `/root/autodl-tmp` is mounted as runtime project disk. Current AutoDL planning rule: prioritize the free server-side runtime space as `80G` class first.
- `/autodl-fs/data` is the mount behind the AutoDL UI label “文件存储”; current planning rule: treat its free shared quota as `20G` class first, and avoid duplicating large assets there and in runtime paths.
- `/autodl-pub/data` may exist as large shared storage.

## Operational Rules Confirmed
1. Place active projects under `/root/autodl-tmp/workspace`.
2. Keep staged uploads and cross-container shared source data in `/autodl-fs/data`.
3. Keep long-running jobs and services in `screen`.
4. Use system/container Python environments, do not create per-project `venv`.

## First-Minute Checklist for New Server
1. `df -hT / /root/autodl-tmp /autodl-fs/data`
2. `nvidia-smi`
3. `screen -ls`
4. `python` path verification, usually `/root/miniconda3/bin/python`
5. Persist findings to local markdown `state.md` and `timeline.md` (optional mirror in remote `server.env`)
