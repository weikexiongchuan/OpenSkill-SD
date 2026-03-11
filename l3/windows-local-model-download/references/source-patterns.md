# Source Patterns

## HuggingFace Slot Pattern
- Use `l3/lora-basemodel-download/scripts/resolve_lora_basemodel_download.py` when the source is a workspace catalog slot such as `NoobAI XL 1.1`.
- Reuse the resolved `repo_id` and `filename`, but override storage and runtime roots for local Windows paths.
- Mirror-based HuggingFace downloads may redirect the actual payload to a different object-storage domain; downloaders must follow redirects and still verify bytes written.

## Civitai Version Pattern
- If the user gives a Civitai model page and version label, first resolve the exact `modelVersionId`.
- Query `https://civitai.com/api/v1/model-versions/<modelVersionId>` to get the exact file entries.
- Prefer the `downloadUrl` field of the matching file entry instead of reconstructing query strings by hand.
- If direct download requests fail over one proxy type, retry with another available proxy type before concluding the source is down.

## Local Activation Pattern
- After download completes, create hard links into local app directories if the user wants the model visible there immediately.
- Do not create activation links while the file is still incomplete.
