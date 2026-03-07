#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError

USER_AGENT = "SDSKILL-RemoteDownloader/1.0"
CHUNK_SIZE = 1024 * 1024


def now_ts() -> float:
    return round(time.time(), 3)


def emit(status_file: Optional[Path], event: str, **payload: object) -> None:
    body = {"event": event, "ts": now_ts(), **payload}
    line = json.dumps(body, ensure_ascii=False)
    print(line, flush=True)
    if status_file is not None:
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with status_file.open("a", encoding="utf-8") as file:
            file.write(line + "\n")
            file.flush()


def human_bytes(num: float) -> str:
    value = float(num)
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{int(num)} B"


def make_request(url: str, method: str = "GET", start: Optional[int] = None):
    headers = {"User-Agent": USER_AGENT}
    if start is not None and start > 0:
        headers["Range"] = f"bytes={start}-"
    req = urllib.request.Request(url, headers=headers, method=method)
    return urllib.request.urlopen(req, timeout=60)


def detect_total_size(url: str) -> int:
    try:
        with make_request(url, method="HEAD") as response:
            length = response.headers.get("Content-Length")
            if length:
                return int(length)
    except Exception:
        pass

    try:
        with make_request(url, method="GET", start=0) as response:
            content_range = response.headers.get("Content-Range", "")
            if "/" in content_range:
                return int(content_range.rsplit("/", 1)[1])
            length = response.headers.get("Content-Length")
            if length:
                return int(length)
    except Exception as exc:
        raise RuntimeError(f"failed to detect remote size: {exc}") from exc

    raise RuntimeError("remote size unavailable")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download one file from HF mirror on the remote server with progress events.")
    parser.add_argument("url")
    parser.add_argument("output_path")
    parser.add_argument("--warmup-seconds", type=int, default=6)
    parser.add_argument("--report-interval", type=int, default=15)
    parser.add_argument("--status-file", default="")
    args = parser.parse_args()

    output_path = Path(args.output_path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = output_path.with_suffix(output_path.suffix + ".part")
    status_file = Path(args.status_file).expanduser() if args.status_file else None

    try:
        total_size = detect_total_size(args.url)
        emit(status_file, "size", bytes=total_size, human=human_bytes(total_size), path=str(output_path))

        if output_path.exists() and output_path.stat().st_size == total_size:
            emit(
                status_file,
                "done",
                elapsed_seconds=0,
                downloaded_bytes=total_size,
                downloaded_human=human_bytes(total_size),
                total_bytes=total_size,
                total_human=human_bytes(total_size),
                average_speed_bps=0,
                average_speed_human="0 B/s",
                path=str(output_path),
                reused_existing=True,
            )
            return 0

        existing = part_path.stat().st_size if part_path.exists() else 0
        emit(status_file, "start", existing_bytes=existing, existing_human=human_bytes(existing), path=str(part_path))

        response = None
        append_mode = False
        if existing > 0:
            try:
                response = make_request(args.url, start=existing)
                append_mode = getattr(response, "status", None) == 206
                if not append_mode:
                    response.close()
                    response = None
                    existing = 0
                    if part_path.exists():
                        part_path.unlink()
            except (HTTPError, URLError):
                existing = 0
                if part_path.exists():
                    part_path.unlink()

        if response is None:
            response = make_request(args.url)
            append_mode = False

        started_at = time.time()
        last_report_at = started_at
        last_report_bytes = existing
        warmup_done = False
        downloaded = existing
        mode = "ab" if append_mode and existing > 0 else "wb"

        with response, part_path.open(mode) as output:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                output.write(chunk)
                downloaded += len(chunk)
                now = time.time()
                elapsed = max(now - started_at, 1e-6)

                if not warmup_done and elapsed >= args.warmup_seconds:
                    avg_speed = max((downloaded - existing) / elapsed, 1e-6)
                    remaining = max(total_size - downloaded, 0)
                    emit(
                        status_file,
                        "warmup",
                        elapsed_seconds=round(elapsed, 2),
                        downloaded_bytes=downloaded,
                        downloaded_human=human_bytes(downloaded),
                        total_bytes=total_size,
                        total_human=human_bytes(total_size),
                        average_speed_bps=avg_speed,
                        average_speed_human=f"{human_bytes(avg_speed)}/s",
                        eta_seconds=round(remaining / avg_speed, 2),
                    )
                    warmup_done = True

                if now - last_report_at >= args.report_interval:
                    interval = max(now - last_report_at, 1e-6)
                    current_speed = max((downloaded - last_report_bytes) / interval, 1e-6)
                    avg_speed = max((downloaded - existing) / elapsed, 1e-6)
                    remaining = max(total_size - downloaded, 0)
                    emit(
                        status_file,
                        "progress",
                        elapsed_seconds=round(elapsed, 2),
                        downloaded_bytes=downloaded,
                        downloaded_human=human_bytes(downloaded),
                        total_bytes=total_size,
                        total_human=human_bytes(total_size),
                        percent=round((downloaded / total_size) * 100, 2) if total_size else 0,
                        current_speed_bps=current_speed,
                        current_speed_human=f"{human_bytes(current_speed)}/s",
                        average_speed_bps=avg_speed,
                        average_speed_human=f"{human_bytes(avg_speed)}/s",
                        eta_seconds=round(remaining / avg_speed, 2),
                    )
                    last_report_at = now
                    last_report_bytes = downloaded

        os.replace(part_path, output_path)
        total_elapsed = max(time.time() - started_at, 1e-6)
        avg_speed = max((downloaded - existing) / total_elapsed, 1e-6)
        emit(
            status_file,
            "done",
            elapsed_seconds=round(total_elapsed, 2),
            downloaded_bytes=downloaded,
            downloaded_human=human_bytes(downloaded),
            total_bytes=total_size,
            total_human=human_bytes(total_size),
            average_speed_bps=avg_speed,
            average_speed_human=f"{human_bytes(avg_speed)}/s",
            path=str(output_path),
            reused_existing=False,
        )
        return 0
    except Exception as exc:
        emit(status_file, "error", message=str(exc), path=str(output_path))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
