# ComfyUI Field Validated Notes

## Validation Context
Flow verified on real AutoDL server with workspace under `/root/autodl-tmp/workspace`.

## Branch Outcome Observed
- Precheck showed app directory existed, but service was not running.
- Direct start (`python main.py`) failed first due to missing dependency: `ModuleNotFoundError: sqlalchemy`.
- Install branch in system environment resolved dependencies.
- Second start succeeded and API health on `127.0.0.1:8188` became healthy.

## Practical Timing Notes
- A running `screen` session does not guarantee API readiness.
- `HEALTH_8188` can remain `no` for a short warm-up window after process start.
- Always perform at least one delayed health recheck before declaring failure.

## Environment Notes
- System Python path worked: `/root/miniconda3/bin/python`.
- Torch may already exist in image; still run `pip install -r requirements.txt` when direct start fails.
- Expected warning may appear:
  - `need pytorch with cu130 or higher` for certain optimized kernels.
  - This is not necessarily a startup blocker.

## Stable Minimal Runtime Pattern
1. Precheck (running + health + app presence).
2. Try direct start.
3. If import/dependency failure, run install in system environment.
4. Restart with `python main.py` in `screen`.
5. Healthcheck `127.0.0.1:8188`, then handoff for AutoDL port mapping.
