#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs(base: Path) -> None:
    (base / "login").mkdir(parents=True, exist_ok=True)
    (base / "services").mkdir(parents=True, exist_ok=True)
    (base / "training").mkdir(parents=True, exist_ok=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_timeline(base: Path, line: str) -> None:
    timeline = base / "timeline.md"
    if not timeline.exists():
        write(timeline, "# Timeline\n\n")
    with timeline.open("a", encoding="utf-8") as f:
        f.write(f"- {now_iso()} {line}\n")


def main() -> int:
    p = argparse.ArgumentParser(description="Record local markdown server state.")
    p.add_argument("workspace_root")
    p.add_argument("server_alias")
    p.add_argument("host")
    p.add_argument("port")
    p.add_argument("user")
    p.add_argument("login_method", choices=["key", "password"])
    p.add_argument("remote_workspace_root")
    p.add_argument("identity_file", nargs="?", default="")
    p.add_argument("ssh_alias", nargs="?", default="")
    p.add_argument("status", nargs="?", default="active")
    args = p.parse_args()

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    ensure_dirs(base)

    state_text = (
        f"# Server State: {args.server_alias}\n\n"
        f"## Connection\n"
        f"- Host: {args.host}\n"
        f"- Port: {args.port}\n"
        f"- User: {args.user}\n\n"
        f"## Login Mode\n"
        f"- Method: {args.login_method}\n"
        f"- Identity File: {args.identity_file}\n"
        f"- SSH Alias: {args.ssh_alias}\n\n"
        f"## Runtime\n"
        f"- Workspace Root: {args.remote_workspace_root}\n"
        f"- Last Verified: {now_iso()}\n"
        f"- Status: {args.status}\n"
    )
    write(base / "state.md", state_text)

    login_text = (
        "# Login Method\n\n"
        f"- Method: {args.login_method}\n"
        "- Password Stored: no\n"
        f"- Identity File: {args.identity_file}\n"
        f"- SSH Alias: {args.ssh_alias}\n"
        f"- Updated At: {now_iso()}\n"
    )
    write(base / "login" / "method.md", login_text)

    append_timeline(base, f"updated server state ({args.host}:{args.port}, login={args.login_method}).")
    print(f"updated markdown state: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
