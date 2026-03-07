#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    p = argparse.ArgumentParser(description="Record login mode in local markdown workspace.")
    p.add_argument("workspace_root")
    p.add_argument("server_alias")
    p.add_argument("login_method", choices=["key", "password"])
    p.add_argument("identity_file", nargs="?", default="")
    p.add_argument("ssh_alias", nargs="?", default="")
    args = p.parse_args()

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    (base / "login").mkdir(parents=True, exist_ok=True)

    text = (
        "# Login Method\n\n"
        f"- Method: {args.login_method}\n"
        "- Password Stored: no\n"
        f"- Identity File: {args.identity_file}\n"
        f"- SSH Alias: {args.ssh_alias}\n"
        f"- Updated At: {now_iso()}\n"
    )
    (base / "login" / "method.md").write_text(text, encoding="utf-8")

    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as f:
        f.write(f"- {now_iso()} updated login mode to {args.login_method}.\n")

    print(f"updated login markdown: {base / 'login' / 'method.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
