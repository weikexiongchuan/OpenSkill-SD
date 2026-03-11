# Windows Local Download Playbook

## Scope
- This skill covers local Windows predownload flows for large checkpoint or base-model files.
- Preferred behavior is resumable download into one persistent path, followed by optional hard-link activation into local app directories.

## Core Rules
- Do not judge progress by process lifetime alone.
- Always inspect bytes written on disk when the file is large.
- Prefer resumable Python download scripts over a single long curl command.
- When the user wants the model visible in both `ComfyUI` and `lora-scripts`, create hard links instead of duplicate copies.

## Source Modes
- `hf-slot`: first resolve one exact HuggingFace slot with `l3/lora-basemodel-download`, then download the resolved `repo_id` and `filename`.
- `hf-url`: download from one explicit HuggingFace URL or mirror URL.
- `civitai-version`: resolve one Civitai model-version id to the exact file entry, then download its `downloadUrl`.

## Persistent Path Rule
- Store the primary file under `<workspace-root>/models/checkpoints/<model-subdir>/<filename>`.
- Keep app-specific activation paths separate from the persistent store.

## Activation Rule
- `ComfyUI` checkpoint target: `<workspace-root>/ComfyUI/models/checkpoints/<filename>`
- `lora-scripts` checkpoint target: `<workspace-root>/lora-scripts/sd-models/<filename>`
- Use hard links by default on Windows local.

## Progress Policy
1. Resolve one exact file target and expected total size if available.
2. Start the resumable downloader.
3. Sample the target `.part` file or final file size on disk.
4. Report speed and ETA from byte growth, not from downloader log lines alone.
5. After completion, verify the final file exists at the persistent path.
6. Create hard links only after the final file is complete.
