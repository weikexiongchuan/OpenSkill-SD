# Download Recipes

## Precheck
```bash
[ -f /etc/network_turbo ] && echo "network_turbo available" || echo "network_turbo missing"
```

## GitHub Clone with Built-In Acceleration
```bash
source /etc/network_turbo
git clone https://github.com/<owner>/<repo>.git
```

## GitHub Clone with Public Proxy
```bash
git clone https://ghproxy.link/https://github.com/<owner>/<repo>.git
```

## HuggingFace CLI with Mirror Endpoint
```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download <repo_id> --local-dir <target_dir>
```

## `hf download` with Mirror Endpoint
```bash
export HF_ENDPOINT=https://hf-mirror.com
hf download <repo_id> <filename> --local-dir <target_dir>
```

## Basemodel Example via HF Mirror
```bash
export HF_ENDPOINT=https://hf-mirror.com
hf download Laxhar/noobai-XL-1.1 NoobAI-XL-v1.1.safetensors \
  --local-dir /autodl-fs/data/models/noobai-xl-1.1
```

## Snapshot Download (Python)
```python
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import snapshot_download
snapshot_download(repo_id="<repo_id>", local_dir="<target_dir>")
```

## Download Window Pattern
1. Enable acceleration.
2. Execute download commands.
3. Validate files.
4. Disable acceleration immediately.

## Mirror Notes
- `HF_ENDPOINT=https://hf-mirror.com` can be used for HuggingFace-hosted repos without changing the repo id itself.
- If the target repo is gated or requires a token, mirror access still needs the corresponding HuggingFace authentication.
- Large model files should still land in `/autodl-fs/data/...` first and only sync to `/root/autodl-tmp/...` when runtime performance actually needs it.
