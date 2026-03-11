import argparse
import os
import time
from pathlib import Path

import requests


def format_size(num_bytes: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{num_bytes} B"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resumable URL downloader")
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--proxy", default="")
    parser.add_argument("--user-agent", default="Mozilla/5.0")
    parser.add_argument("--chunk-size", type=int, default=8 * 1024 * 1024)
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = output_path.with_suffix(output_path.suffix + ".part")

    proxies = None
    if args.proxy:
        proxies = {"http": args.proxy, "https": args.proxy}

    existing = part_path.stat().st_size if part_path.exists() else 0
    headers = {"User-Agent": args.user_agent}
    if existing > 0:
        headers["Range"] = f"bytes={existing}-"

    with requests.get(
        args.url,
        headers=headers,
        proxies=proxies,
        stream=True,
        timeout=(20, 120),
        allow_redirects=True,
    ) as resp:
        resp.raise_for_status()
        if existing > 0 and resp.status_code != 206:
            existing = 0

        total = None
        content_range = resp.headers.get("Content-Range")
        if content_range and "/" in content_range:
            total = int(content_range.split("/")[-1])
        elif resp.headers.get("Content-Length"):
            total = existing + int(resp.headers["Content-Length"])

        mode = "ab" if existing > 0 else "wb"
        downloaded = existing
        last_report = time.time()
        last_bytes = downloaded
        last_time = last_report

        with open(part_path, mode) as f:
            for chunk in resp.iter_content(chunk_size=args.chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                now = time.time()
                if now - last_report >= 5:
                    speed = (downloaded - last_bytes) / max(now - last_time, 1e-6)
                    if total:
                        pct = downloaded / total * 100
                        eta = (total - downloaded) / speed if speed > 0 else 0
                        print(
                            f"progress={pct:.2f}% downloaded={format_size(downloaded)} "
                            f"total={format_size(total)} speed={format_size(speed)}/s eta={eta/60:.1f}m",
                            flush=True,
                        )
                    else:
                        print(
                            f"downloaded={format_size(downloaded)} speed={format_size(speed)}/s",
                            flush=True,
                        )
                    last_report = now
                    last_bytes = downloaded
                    last_time = now

    os.replace(part_path, output_path)
    print(f"done={output_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
