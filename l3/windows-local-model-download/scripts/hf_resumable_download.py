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


def resolve_final_url(repo_id: str, filename: str, endpoint: str) -> str:
    from huggingface_hub import hf_hub_url

    url = hf_hub_url(repo_id=repo_id, filename=filename, endpoint=endpoint)
    resp = requests.get(url, allow_redirects=False, timeout=(20, 60))
    resp.raise_for_status()
    if resp.is_redirect and resp.headers.get("location"):
        return resp.headers["location"]
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Resumable Hugging Face file downloader")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--filename", required=True)
    parser.add_argument("--endpoint", default="https://hf-mirror.com")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--chunk-size", type=int, default=8 * 1024 * 1024)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / args.filename
    part_path = output_dir / f"{args.filename}.part"

    final_url = resolve_final_url(args.repo_id, args.filename, args.endpoint)
    existing = part_path.stat().st_size if part_path.exists() else 0
    headers = {}
    if existing > 0:
        headers["Range"] = f"bytes={existing}-"

    with requests.get(final_url, headers=headers, stream=True, timeout=(20, 120)) as resp:
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

    os.replace(part_path, final_path)
    print(f"done={final_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
