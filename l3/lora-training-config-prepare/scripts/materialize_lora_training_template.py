#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_FILE = ROOT / "l1" / "lora-scripts-beginner-parameter-playbook" / "references" / "training-templates.yaml"
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?$")

COMMON_DEFAULTS = {
    "sdxl-lora": {
        "model_train_type": "sdxl-lora",
        "enable_bucket": True,
        "min_bucket_reso": 256,
        "max_bucket_reso": 1024,
        "bucket_reso_steps": 64,
        "bucket_no_upscale": True,
        "save_model_as": "safetensors",
        "save_precision": "fp16",
        "save_every_n_epochs": 1,
        "gradient_checkpointing": True,
        "gradient_accumulation_steps": 1,
        "network_train_text_encoder_only": False,
        "learning_rate": 1e-4,
        "lr_scheduler": "constant",
        "lr_warmup_steps": 0,
        "optimizer_type": "AdamW8bit",
        "network_module": "networks.lora",
        "log_with": "tensorboard",
        "logging_dir": "./logs",
        "caption_extension": ".txt",
        "max_token_length": 255,
        "seed": 1337,
        "mixed_precision": "bf16",
        "xformers": True,
        "sdpa": True,
        "lowram": False,
        "cache_latents": True,
        "cache_latents_to_disk": True,
        "persistent_data_loader_workers": True,
        "output_dir": "/root/autodl-tmp/lora-scripts/output",
        "enable_preview": False,
    }
}


def load_templates() -> list[dict]:
    data = yaml.safe_load(TEMPLATE_FILE.read_text(encoding="utf-8")) or {}
    templates = data.get("templates")
    if not isinstance(templates, list):
        raise SystemExit(f"invalid template file: {TEMPLATE_FILE}")
    return templates


def select_template(template_id: str) -> dict:
    for item in load_templates():
        if str(item.get("id")) == template_id:
            return item
    raise SystemExit(f"template not found: {template_id}")


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


def normalize_starter_values(starter: dict) -> dict:
    return normalize_value(starter)


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize one built-in beginner template into a runnable source config JSON.")
    parser.add_argument("template_id")
    parser.add_argument("output_file")
    parser.add_argument("--output-dir", default="/root/autodl-tmp/lora-scripts/output")
    args = parser.parse_args()

    template = select_template(args.template_id)
    family = str(template.get("family") or "")
    defaults = normalize_value(dict(COMMON_DEFAULTS.get(family, {})))
    if not defaults:
        raise SystemExit(f"unsupported template family: {family}")

    starter = normalize_starter_values(template.get("starter") or {})
    config = defaults
    config.update(starter)
    config["model_train_type"] = defaults["model_train_type"]
    config["output_dir"] = args.output_dir

    output_path = Path(args.output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
