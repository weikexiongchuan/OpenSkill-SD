import argparse
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a hard link for a local model file")
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    target = Path(args.target)
    if not source.exists():
        raise SystemExit(f"source not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"exists={target}")
        return 0
    os.link(source, target)
    print(f"linked={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
