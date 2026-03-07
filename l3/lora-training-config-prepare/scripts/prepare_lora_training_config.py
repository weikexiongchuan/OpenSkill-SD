#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?$")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or "config"


def ensure_dirs(base: Path) -> None:
    (base / "training" / "prepared-configs").mkdir(parents=True, exist_ok=True)
    (base / "training" / "sample-prompts").mkdir(parents=True, exist_ok=True)


def append_timeline(base: Path, line: str) -> None:
    timeline = base / "timeline.md"
    if not timeline.exists():
        timeline.write_text("# Timeline\n\n", encoding="utf-8")
    with timeline.open("a", encoding="utf-8") as file:
        file.write(f"- {now_iso()} {line}\n")


def load_registered_lines(registry_file: Path) -> list[str]:
    if not registry_file.exists():
        return []
    marker = "## Registered Configs\n"
    content = registry_file.read_text(encoding="utf-8")
    if marker not in content:
        return []
    block = content.split(marker, 1)[1]
    return [line for line in block.splitlines() if line.startswith("- ")]


def parse_toml(path: Path) -> dict:
    if tomllib is None:
        raise RuntimeError("tomllib is unavailable")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def detect_source_label(path: Path) -> str:
    text = path.as_posix()
    if "manual-import" in text or "/imported-configs/" in text:
        return "manual-import"
    if "/prepared-configs/" in text:
        return "prepared"
    return "other"


def normalize_scalar(value):
    if not isinstance(value, str):
        return value
    text = value.strip()
    if "~" in text:
        left = text.split("~", 1)[0].strip()
        if left:
            return normalize_scalar(left)
    if not NUMERIC_RE.fullmatch(text):
        return value
    if re.fullmatch(r"^[+-]?\d+$", text):
        return int(text)
    return float(text)


def normalize_value(value):
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return normalize_scalar(value)


def load_source_config(path: Path, preset_name: str) -> tuple[dict, dict[str, str]]:
    suffix = path.suffix.lower()
    meta = {
        "file_type": "raw-file",
        "selected_preset": "",
        "parse_status": "raw-copy",
    }
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        meta["parse_status"] = "parsed"
        if isinstance(data, dict):
            meta["file_type"] = "json-config"
            return normalize_value(dict(data)), meta
        if isinstance(data, list):
            meta["file_type"] = "json-history"
            if not data:
                raise SystemExit("json history is empty")
            if preset_name:
                for item in data:
                    if isinstance(item, dict) and item.get("name") == preset_name and isinstance(item.get("value"), dict):
                        meta["selected_preset"] = preset_name
                        return normalize_value(dict(item["value"])), meta
                raise SystemExit(f"preset not found in json history: {preset_name}")
            if len(data) == 1 and isinstance(data[0], dict) and isinstance(data[0].get("value"), dict):
                meta["selected_preset"] = str(data[0].get("name") or "")
                return normalize_value(dict(data[0]["value"])), meta
            raise SystemExit("preset_name is required for json history files with multiple presets")
        raise SystemExit("unsupported json config shape")
    if suffix == ".toml":
        meta["file_type"] = "toml-config"
        meta["parse_status"] = "parsed"
        return normalize_value(dict(parse_toml(path))), meta
    raise SystemExit(f"unsupported config file type: {suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare one LoRA training config for API execution.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("source_config_file")
    parser.add_argument("base_model_path")
    parser.add_argument("train_data_dir")
    parser.add_argument("output_name")
    parser.add_argument("prepared_name", nargs="?", default="")
    parser.add_argument("notes", nargs="?", default="")
    parser.add_argument("--preset-name", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--sample-prompt-file", default="")
    parser.add_argument("--sample-every-n-epochs", type=int, default=1)
    parser.add_argument("--sample-sampler", default="euler_a")
    args = parser.parse_args()

    source = Path(args.source_config_file).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise SystemExit(f"config file not found: {source}")

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    ensure_dirs(base)

    config, meta = load_source_config(source, args.preset_name)
    config["pretrained_model_name_or_path"] = args.base_model_path
    config["train_data_dir"] = args.train_data_dir
    config["output_name"] = args.output_name
    if args.output_dir:
        config["output_dir"] = args.output_dir
    if args.sample_prompt_file:
        sample_prompt_file = Path(args.sample_prompt_file).expanduser().resolve()
        if not sample_prompt_file.exists() or not sample_prompt_file.is_file():
            raise SystemExit(f"sample prompt file not found: {sample_prompt_file}")
        config["prompt_file"] = str(sample_prompt_file)
        config["sample_every_n_epochs"] = args.sample_every_n_epochs
        config["sample_sampler"] = args.sample_sampler

    model_train_type = str(config.get("model_train_type") or "")
    if not model_train_type:
        raise SystemExit("model_train_type is missing after config load")

    prepared_name = args.prepared_name or args.output_name or source.stem
    stored_name = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}__prepared__{slugify(prepared_name)}.json"
    stored_path = base / "training" / "prepared-configs" / stored_name
    stored_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry_file = base / "training" / "configs.md"
    history = load_registered_lines(registry_file)
    relative_source = source.relative_to(base).as_posix() if source.is_relative_to(base) else str(source)
    relative_prepared = stored_path.relative_to(base).as_posix()
    source_label = detect_source_label(source)
    history.append(
        f"- {now_iso()} | name={prepared_name} | source={source_label} | stage=prepared | type=json-config | "
        f"model={model_train_type} | output={args.output_name} | preset={meta['selected_preset']} | file={relative_prepared}"
    )
    history_text = "\n".join(history).rstrip() + "\n"

    text = (
        "# LoRA Training Config Registry\n\n"
        "## Latest Config\n"
        f"- Config Name: {prepared_name}\n"
        f"- Source: {source_label}\n"
        "- Stage: prepared\n"
        "- File Type: json-config\n"
        f"- Parse Status: {meta['parse_status']}\n"
        f"- Original Path: {source}\n"
        f"- Stored Path: {relative_source}\n"
        f"- Prepared Path: {relative_prepared}\n"
        f"- Selected Preset: {meta['selected_preset']}\n"
        f"- Model Train Type: {model_train_type}\n"
        f"- Base Model Path: {args.base_model_path}\n"
        f"- Train Data Dir: {args.train_data_dir}\n"
        f"- Output Name: {args.output_name}\n"
        f"- Notes: {args.notes}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Registered Configs\n"
        f"{history_text}"
    )
    registry_file.write_text(text, encoding="utf-8")

    append_timeline(
        base,
        f"prepared LoRA training config (name={prepared_name}, source={source_label}, model={model_train_type}).",
    )
    print(stored_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
