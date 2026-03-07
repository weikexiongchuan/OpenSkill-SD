#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    p = argparse.ArgumentParser(description="Record ComfyUI state in local markdown workspace.")
    p.add_argument("workspace_root")
    p.add_argument("server_alias")
    p.add_argument("session")
    p.add_argument("service_port")
    p.add_argument("access_mode", choices=["public-port", "ssh-tunnel-cli", "ssh-tunnel-gui"])
    p.add_argument("service_url")
    p.add_argument("health", choices=["ok", "failed", "unknown"])
    args = p.parse_args()

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    (base / "services").mkdir(parents=True, exist_ok=True)

    text = (
        "# ComfyUI Service\n\n"
        f"- Session: {args.session}\n"
        f"- Service Port: {args.service_port}\n"
        f"- Access Mode: {args.access_mode}\n"
        f"- Service URL: {args.service_url}\n"
        f"- Health: {args.health}\n"
        f"- Updated At: {now_iso()}\n"
    )
    (base / "services" / "comfyui.md").write_text(text, encoding="utf-8")

    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as f:
        f.write(f"- {now_iso()} updated ComfyUI state ({args.health}) on port {args.service_port}.\n")

    print(f"updated comfyui markdown: {base / 'services' / 'comfyui.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
