#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List

try:
    from PIL import Image, ImageOps
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(f"Pillow is required on the remote host: {exc}")

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def is_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def stem_key(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    return str((rel.parent / rel.stem).as_posix())


def floor_multiple_64(value: int) -> int:
    return value - (value % 64)


def ceil_multiple_64(value: int) -> int:
    return ((value + 63) // 64) * 64


def has_alpha(image: Image.Image) -> bool:
    return "A" in image.getbands()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_image(image: Image.Image, target: Path, source_suffix: str) -> None:
    ensure_parent(target)
    temp = target.with_name(target.name + ".tmp")
    suffix = source_suffix.lower()
    out = image
    kwargs: Dict[str, object] = {}
    if suffix in {".jpg", ".jpeg"}:
        if out.mode not in {"RGB", "L"}:
            out = out.convert("RGB")
        kwargs = {"format": "JPEG", "quality": 95, "subsampling": 0}
    elif suffix == ".png":
        if out.mode == "P":
            out = out.convert("RGBA")
        kwargs = {"format": "PNG"}
    elif suffix == ".webp":
        if out.mode not in {"RGB", "RGBA"}:
            out = out.convert("RGBA" if has_alpha(out) else "RGB")
        kwargs = {"format": "WEBP", "quality": 95}
    elif suffix == ".bmp":
        if out.mode not in {"RGB", "L"}:
            out = out.convert("RGB")
        kwargs = {"format": "BMP"}
    else:
        kwargs = {}
    out.save(temp, **kwargs)
    temp.replace(target)


def build_padded_image(image: Image.Image, width: int, height: int) -> Image.Image:
    base_mode = "RGBA" if has_alpha(image) else "RGB"
    source = image if image.mode == base_mode else image.convert(base_mode)
    fill = (255, 255, 255, 255) if base_mode == "RGBA" else (255, 255, 255)
    canvas = Image.new(base_mode, (width, height), fill)
    offset_x = (width - source.width) // 2
    offset_y = (height - source.height) // 2
    if base_mode == "RGBA":
        canvas.paste(source, (offset_x, offset_y), source)
    else:
        canvas.paste(source, (offset_x, offset_y))
    return canvas


def transform_image(image_path: Path, target_path: Path, size_policy: str) -> tuple[str, str]:
    with Image.open(image_path) as opened:
        image = ImageOps.exif_transpose(opened)
        width, height = image.size
        if width % 64 == 0 and height % 64 == 0:
            if target_path != image_path:
                ensure_parent(target_path)
                shutil.copy2(image_path, target_path)
            return "ok", f"{width}x{height}"

        if size_policy == "check-only":
            if target_path != image_path:
                ensure_parent(target_path)
                shutil.copy2(image_path, target_path)
            return "needs-resize", f"{width}x{height}"

        if size_policy == "crop":
            new_width = floor_multiple_64(width)
            new_height = floor_multiple_64(height)
            if new_width < 64 or new_height < 64:
                if target_path != image_path:
                    ensure_parent(target_path)
                    shutil.copy2(image_path, target_path)
                return "crop-too-small", f"{width}x{height}"
            left = (width - new_width) // 2
            top = (height - new_height) // 2
            transformed = image.crop((left, top, left + new_width, top + new_height))
            save_image(transformed, target_path, image_path.suffix)
            return "resized", f"{width}x{height}->{new_width}x{new_height}"

        if size_policy == "pad-white":
            new_width = ceil_multiple_64(width)
            new_height = ceil_multiple_64(height)
            transformed = build_padded_image(image, new_width, new_height)
            save_image(transformed, target_path, image_path.suffix)
            return "resized", f"{width}x{height}->{new_width}x{new_height}"

        raise SystemExit(f"unsupported size_policy: {size_policy}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check and normalize one remote LoRA training dataset.")
    parser.add_argument("dataset_root")
    parser.add_argument("--size-policy", choices=["crop", "pad-white", "check-only"], default="crop")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--max-issues", type=int, default=20)
    args = parser.parse_args()

    root = Path(args.dataset_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"dataset directory not found: {root}")

    runtime_root = Path(args.output_dir).expanduser().resolve() if args.output_dir else root
    runtime_root.mkdir(parents=True, exist_ok=True)

    image_paths: List[Path] = []
    caption_paths: List[Path] = []
    image_map: Dict[str, List[Path]] = {}
    caption_map: Dict[str, List[Path]] = {}

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if is_hidden(rel):
            continue
        suffix = path.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            image_paths.append(path)
            image_map.setdefault(stem_key(root, path), []).append(path)
        elif suffix == ".txt":
            caption_paths.append(path)
            caption_map.setdefault(stem_key(root, path), []).append(path)

    issue_samples: List[str] = []

    def push_issue(text: str) -> None:
        if len(issue_samples) < args.max_issues:
            issue_samples.append(text)

    duplicate_image_key_count = 0
    duplicate_caption_key_count = 0
    for key, paths in image_map.items():
        if len(paths) > 1:
            duplicate_image_key_count += 1
            push_issue(f"duplicate-image-key:{key}")
    for key, paths in caption_map.items():
        if len(paths) > 1:
            duplicate_caption_key_count += 1
            push_issue(f"duplicate-caption-key:{key}")

    image_keys = set(image_map)
    caption_keys = set(caption_map)
    missing_keys = sorted(image_keys - caption_keys)
    orphan_keys = sorted(caption_keys - image_keys)

    for key in missing_keys:
        first = image_map[key][0]
        push_issue(f"missing-caption:{first.relative_to(root).as_posix()}")
    for key in orphan_keys:
        first = caption_map[key][0]
        push_issue(f"orphan-caption:{first.relative_to(root).as_posix()}")

    if runtime_root != root:
        for caption_path in caption_paths:
            dest = runtime_root / caption_path.relative_to(root)
            ensure_parent(dest)
            shutil.copy2(caption_path, dest)

    multiple_of_64_ok_count = 0
    needs_resize_count = 0
    resized_count = 0
    resize_error_count = 0

    for image_path in image_paths:
        dest = runtime_root / image_path.relative_to(root) if runtime_root != root else image_path
        outcome, detail = transform_image(image_path, dest, args.size_policy)
        if outcome == "ok":
            multiple_of_64_ok_count += 1
        elif outcome == "needs-resize":
            needs_resize_count += 1
            push_issue(f"needs-resize:{image_path.relative_to(root).as_posix()}:{detail}")
        elif outcome == "resized":
            resized_count += 1
            push_issue(f"resized:{image_path.relative_to(root).as_posix()}:{detail}")
        else:
            resize_error_count += 1
            push_issue(f"resize-error:{image_path.relative_to(root).as_posix()}:{detail}")

    paired_count = sum(
        1
        for key in image_keys & caption_keys
        if len(image_map.get(key, [])) == 1 and len(caption_map.get(key, [])) == 1
    )

    caption_issue = bool(missing_keys or orphan_keys or duplicate_image_key_count or duplicate_caption_key_count)
    unresolved_size_issue = bool(resize_error_count or (needs_resize_count and args.size_policy == "check-only"))

    if caption_issue:
        status = "needs-captions"
    elif unresolved_size_issue:
        status = "needs-size-fix"
    elif resized_count > 0 or runtime_root != root:
        status = "prepared"
    else:
        status = "ready"

    summary = {
        "root_dir": str(root),
        "runtime_dir": str(runtime_root),
        "size_policy": args.size_policy,
        "image_count": len(image_paths),
        "caption_count": len(caption_paths),
        "paired_count": paired_count,
        "missing_caption_count": len(missing_keys),
        "orphan_caption_count": len(orphan_keys),
        "duplicate_image_key_count": duplicate_image_key_count,
        "duplicate_caption_key_count": duplicate_caption_key_count,
        "multiple_of_64_ok_count": multiple_of_64_ok_count,
        "needs_resize_count": needs_resize_count,
        "resized_count": resized_count,
        "resize_error_count": resize_error_count,
        "status": status,
        "ready": status in {"ready", "prepared"},
        "sample_issues": issue_samples,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
