# Windows Local ComfyUI Operations

## Local Defaults
- App dir: `<workspace-root>/ComfyUI`
- Local URL: `http://127.0.0.1:8188`
- Log file: `<workspace-root>/comfyui.log`

## Environment Policy
- Prefer a dedicated conda env for ComfyUI.
- Reuse an existing Python `3.11` env when possible.
- Do not force ComfyUI to share the same env with `lora-scripts`, because ComfyUI currently wants `transformers>=4.50.3` while `lora-scripts` pins `transformers==4.44.0`.

## Reference Baseline
- Use one dedicated Python `3.11` conda env for ComfyUI.
- Install GPU Torch as `torch==2.7.1+cu118`, `torchvision==0.22.1+cu118`, `torchaudio==2.7.1+cu118`
- Expect the local service check on `http://127.0.0.1:8188` to return HTTP `200`

## Reuse Flow
1. Check whether a reusable env already exists.
2. If the env has CPU Torch only, reinstall GPU Torch in place.
3. Install `requirements.txt`.
4. Start ComfyUI on `127.0.0.1:8188`.
5. Verify the local HTTP endpoint.

## Example Commands
```powershell
conda run -n <comfyui-env> python -m pip install --upgrade --force-reinstall torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118
conda run -n <comfyui-env> python -m pip install -r <workspace-root>\ComfyUI\requirements.txt
conda run -n <comfyui-env> python <workspace-root>\ComfyUI\main.py --listen 127.0.0.1 --port 8188
```

## Health Check
```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8188
```

## If No Reusable Env Exists
- Switch to `l3/windows-conda-sd-env-prepare`.
- Create a dedicated Python `3.11` env for ComfyUI first, then install GPU Torch and `requirements.txt`.
