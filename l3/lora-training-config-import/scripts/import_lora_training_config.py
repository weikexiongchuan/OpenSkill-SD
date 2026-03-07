#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or "config"


def ensure_dirs(base: Path) -> None:
    (base / "training" / "imported-configs").mkdir(parents=True, exist_ok=True)


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


def summarize_config(path: Path) -> dict[str, str]:
    suffix = path.suffix.lower()
    summary = {
        "file_type": "raw-file",
        "config_name": path.stem,
        "model_train_type": "",
        "base_model_path": "",
        "train_data_dir": "",
        "output_name": "",
        "preset_count": "",
        "preset_names": "",
        "parse_status": "raw-copy",
    }
    try:
        if suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            summary["parse_status"] = "parsed"
            if isinstance(data, dict):
                summary["file_type"] = "json-config"
                summary["config_name"] = data.get("output_name") or path.stem
                summary["model_train_type"] = str(data.get("model_train_type") or "")
                summary["base_model_path"] = str(data.get("pretrained_model_name_or_path") or "")
                summary["train_data_dir"] = str(data.get("train_data_dir") or "")
                summary["output_name"] = str(data.get("output_name") or "")
            elif isinstance(data, list):
                summary["file_type"] = "json-history"
                names = []
                models = []
                outputs = []
                base_models = []
                data_dirs = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name")
                    if name:
                        names.append(str(name))
                    value = item.get("value") if isinstance(item.get("value"), dict) else {}
                    model = value.get("model_train_type")
                    output = value.get("output_name")
                    base_model = value.get("pretrained_model_name_or_path")
                    data_dir = value.get("train_data_dir")
                    if model:
                        models.append(str(model))
                    if output:
                        outputs.append(str(output))
                    if base_model:
                        base_models.append(str(base_model))
                    if data_dir:
                        data_dirs.append(str(data_dir))
                summary["preset_count"] = str(len(names)) if names else str(len(data))
                summary["preset_names"] = ", ".join(names[:5])
                summary["config_name"] = path.stem
                summary["model_train_type"] = models[0] if len(set(models)) == 1 and models else ""
                summary["output_name"] = outputs[0] if len(set(outputs)) == 1 and outputs else ""
                summary["base_model_path"] = base_models[0] if len(set(base_models)) == 1 and base_models else ""
                summary["train_data_dir"] = data_dirs[0] if len(set(data_dirs)) == 1 and data_dirs else ""
            else:
                summary["file_type"] = "json-unknown"
        elif suffix == ".toml":
            data = parse_toml(path)
            summary["file_type"] = "toml-config"
            summary["parse_status"] = "parsed"
            summary["config_name"] = str(data.get("output_name") or path.stem)
            summary["model_train_type"] = str(data.get("model_train_type") or "")
            summary["base_model_path"] = str(data.get("pretrained_model_name_or_path") or "")
            summary["train_data_dir"] = str(data.get("train_data_dir") or "")
            summary["output_name"] = str(data.get("output_name") or "")
    except Exception:
        pass
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Import one LoRA training config into local server workspace.")
    parser.add_argument("workspace_root")
    parser.add_argument("server_alias")
    parser.add_argument("config_file")
    parser.add_argument("config_name", nargs="?", default="")
    parser.add_argument("notes", nargs="?", default="")
    args = parser.parse_args()

    source = Path(args.config_file).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise SystemExit(f"config file not found: {source}")

    base = Path(args.workspace_root).expanduser().resolve() / "servers" / args.server_alias
    ensure_dirs(base)

    summary = summarize_config(source)
    config_name = args.config_name or summary["config_name"] or source.stem
    stored_name = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}__manual-import__{slugify(config_name)}{source.suffix.lower()}"
    stored_path = base / "training" / "imported-configs" / stored_name
    shutil.copy2(source, stored_path)

    registry_file = base / "training" / "configs.md"
    history = load_registered_lines(registry_file)
    relative_file = stored_path.relative_to(base).as_posix()
    history.append(
        f"- {now_iso()} | name={config_name} | source=manual-import | stage=imported | type={summary['file_type']} | "
        f"model={summary['model_train_type']} | output={summary['output_name']} | presets={summary['preset_count']} | file={relative_file}"
    )
    history_text = "\n".join(history).rstrip() + "\n"

    text = (
        "# LoRA Training Config Registry\n\n"
        "## Latest Config\n"
        f"- Config Name: {config_name}\n"
        "- Source: manual-import\n"
        "- Stage: imported\n"
        f"- File Type: {summary['file_type']}\n"
        f"- Parse Status: {summary['parse_status']}\n"
        f"- Original Path: {source}\n"
        f"- Stored Path: {relative_file}\n"
        "- Prepared Path: \n"
        "- Selected Preset: \n"
        f"- Model Train Type: {summary['model_train_type']}\n"
        f"- Base Model Path: {summary['base_model_path']}\n"
        f"- Train Data Dir: {summary['train_data_dir']}\n"
        f"- Output Name: {summary['output_name']}\n"
        f"- Notes: {args.notes}\n"
        f"- Updated At: {now_iso()}\n\n"
        "## Registered Configs\n"
        f"{history_text}"
    )
    registry_file.write_text(text, encoding="utf-8")

    append_timeline(
        base,
        f"imported LoRA training config (name={config_name}, source=manual-import, type={summary['file_type']}).",
    )
    print(stored_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
