#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from urllib import error, parse, request


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip('/')


def http_json(method: str, url: str, body: Optional[bytes] = None) -> int:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url=url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req) as resp:
            payload = resp.read().decode('utf-8', errors='replace')
            print(payload)
            return 0
    except error.HTTPError as exc:
        payload = exc.read().decode('utf-8', errors='replace')
        print(payload or str(exc), file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(str(exc), file=sys.stderr)
        return 2


def cmd_start(args: argparse.Namespace) -> int:
    config_path = Path(args.config_file)
    if not config_path.exists():
        print(f'config file not found: {config_path}', file=sys.stderr)
        return 2
    try:
        config = json.loads(config_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        print(f'invalid json: {exc}', file=sys.stderr)
        return 2
    if not isinstance(config, dict):
        print('config json must be an object', file=sys.stderr)
        return 2
    body = json.dumps(config, ensure_ascii=False).encode('utf-8')
    url = normalize_base_url(args.base_url) + '/api/run'
    return http_json('POST', url, body)


def cmd_tasks(args: argparse.Namespace) -> int:
    url = normalize_base_url(args.base_url) + '/api/tasks'
    return http_json('GET', url)


def cmd_terminate(args: argparse.Namespace) -> int:
    task_id = parse.quote(args.task_id, safe='')
    url = normalize_base_url(args.base_url) + f'/api/tasks/terminate/{task_id}'
    return http_json('GET', url)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Manage lora-scripts training tasks via web API')
    sub = parser.add_subparsers(dest='command', required=True)

    start = sub.add_parser('start', help='start one training task via /api/run')
    start.add_argument('--base-url', default='http://127.0.0.1:28000')
    start.add_argument('--config-file', required=True)
    start.set_defaults(func=cmd_start)

    tasks = sub.add_parser('tasks', help='list tasks via /api/tasks')
    tasks.add_argument('--base-url', default='http://127.0.0.1:28000')
    tasks.set_defaults(func=cmd_tasks)

    terminate = sub.add_parser('terminate', help='terminate one task via /api/tasks/terminate/{task_id}')
    terminate.add_argument('--base-url', default='http://127.0.0.1:28000')
    terminate.add_argument('--task-id', required=True)
    terminate.set_defaults(func=cmd_terminate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
