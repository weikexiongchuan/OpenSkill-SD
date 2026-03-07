# Workspace Layout

## Recommended Root
Use one local root, for example:
- `/Users/kumakawa/Desktop/SDSKILL/workspace`

## Directory Structure (Markdown-First)
```text
<workspace-root>/
  servers/
    <server-alias>/
      state.md
      timeline.md
      login/
        method.md
      services/
        comfyui.md
        lora-scripts.md
      storage/
        large-files.md
      training/
        lora.md
        models.md
        datasets.md
        configs.md
        sample-prompts.md
        analysis.md
        sample-prompts/
          <timestamp>__sample-prompts__<name>.txt
        imported-configs/
          <timestamp>__manual-import__<config-file>
        prepared-configs/
          <timestamp>__prepared__<config-name>.json
```

## Purpose by Folder
- `state.md`: server summary (host, port, user, current status).
- `login/method.md`: login mode and key alias metadata.
- `services/comfyui.md`: service URL/port and last check result.
- `services/lora-scripts.md`: lora-scripts GUI URL/port and last check result.
- `storage/large-files.md`: per-server large-file registry, including current paths for basemodels, datasets, outputs, and other tracked big assets.
- `training/lora.md`: training runtime state, selected template, task id, and registered run history for this server.
- `training/models.md`: base-model slot registry for this server, including planned/downloaded/manual-upload states.
- `training/datasets.md`: dataset registry for this server, including upload source, remote path, pairing result, and 64-multiple image check result.
- `training/configs.md`: imported training config registry for this server; manual imports must be marked here.
- `training/sample-prompts.md`: latest sample-image prompt strategy for this server, including whether prompts came from random captions or manual input.
- `training/analysis.md`: latest diagnosis report for one LoRA run on this server, plus historical analysis snapshots.
- `training/imported-configs/`: copied user config files kept under the canonical server workspace.
- `training/prepared-configs/`: runnable JSON configs that already bind the current server's base model path and dataset directory.
- `timeline.md`: operation history for traceability.
