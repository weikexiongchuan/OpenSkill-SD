# Windows Local LoRA Scripts Operations

## Local Defaults
- App dir: `<workspace-root>/lora-scripts`
- Local URL: `http://127.0.0.1:28000`
- Tag editor URL: `http://127.0.0.1:28001`
- TensorBoard URL: `http://127.0.0.1:6006`
- Log file: `<workspace-root>/lora-scripts.log`

## Environment Policy
- Prefer a dedicated conda env for lora-scripts.
- Reuse an existing Python `3.10` env when possible.
- Do not force lora-scripts to share the same env with ComfyUI, because lora-scripts currently pins `transformers==4.44.0`.

## Reference Baseline
- Use one dedicated Python `3.10` conda env for lora-scripts.
- Ensure GPU Torch is available before installing the GUI requirements.
- Install `xformers==0.0.30` before the fixed GUI requirements when the selected env does not already contain it.
- Submodules required: `frontend` and `mikazuki/dataset-tag-editor`
- Expect the local service check on `http://127.0.0.1:28000` to return HTTP `200`

## Reuse Flow
1. Check whether a reusable Python `3.10` env already exists.
2. Confirm GPU Torch is available in that env.
3. Ensure `frontend` and `mikazuki/dataset-tag-editor` are present.
4. Install `xformers` and `requirements.txt`.
5. Start the GUI on `127.0.0.1:28000`.
6. Verify the local HTTP endpoint.

## Example Commands
```powershell
conda run -n <lora-scripts-env> python -m pip install -U -I --no-deps xformers==0.0.30 --extra-index-url https://download.pytorch.org/whl/cu118
conda run -n <lora-scripts-env> python -m pip install --upgrade -r <workspace-root>\lora-scripts\requirements.txt
conda run -n <lora-scripts-env> python <workspace-root>\lora-scripts\gui.py --host 127.0.0.1 --port 28000
```

## Health Check
```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:28000
```

## Submodule Requirement
- GUI startup expects `frontend/dist` and `mikazuki/dataset-tag-editor/scripts`.
- If they are missing, repair the submodules before retrying startup.

## If No Reusable Env Exists
- Switch to `l3/windows-conda-sd-env-prepare`.
- Create a dedicated Python `3.10` env for lora-scripts first, then install GPU Torch, `xformers`, and `requirements.txt`.
