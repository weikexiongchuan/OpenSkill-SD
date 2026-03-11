# Windows Conda SD Env Reuse And Create

## Reuse Policy
- Reuse an existing env first when its Python major/minor version fits the target platform.
- Reuse for ComfyUI when the env can carry GPU Torch and modern `transformers`.
- Reuse for lora-scripts when the env is Python `3.10` and can be pinned to the GUI's fixed package set.
- Keep the two platforms in separate envs when their pinned packages diverge.

## Why Separate Envs
- ComfyUI currently accepts newer `transformers` and related packages.
- lora-scripts currently pins `transformers==4.44.0`.
- A shared env causes avoidable upgrades and downgrades during maintenance.

## Reuse Example Pattern
- Reuse one Python `3.11` env for ComfyUI when it can carry GPU Torch and ComfyUI dependencies.
- Reuse one Python `3.10` env for lora-scripts when it can be pinned to the GUI's fixed package set.

## Reuse Commands
### ComfyUI reuse example
```powershell
conda run -n <comfyui-env> python -m pip install --upgrade --force-reinstall torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118
conda run -n <comfyui-env> python -m pip install -r <workspace-root>\ComfyUI\requirements.txt
```

### lora-scripts reuse example
```powershell
conda run -n <lora-scripts-env> python -m pip install -U -I --no-deps xformers==0.0.30 --extra-index-url https://download.pytorch.org/whl/cu118
conda run -n <lora-scripts-env> python -m pip install --upgrade -r <workspace-root>\lora-scripts\requirements.txt
```

## Create Commands
### New ComfyUI env
```powershell
conda create -n comfyui311 python=3.11 -y
conda run -n comfyui311 python -m pip install --upgrade --force-reinstall torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118
conda run -n comfyui311 python -m pip install -r <workspace-root>\ComfyUI\requirements.txt
```

### New lora-scripts env
```powershell
conda create -n lora-scripts310 python=3.10 -y
conda run -n lora-scripts310 python -m pip install --upgrade --force-reinstall torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118
conda run -n lora-scripts310 python -m pip install -U -I --no-deps xformers==0.0.30 --extra-index-url https://download.pytorch.org/whl/cu118
conda run -n lora-scripts310 python -m pip install --upgrade -r <workspace-root>\lora-scripts\requirements.txt
```
