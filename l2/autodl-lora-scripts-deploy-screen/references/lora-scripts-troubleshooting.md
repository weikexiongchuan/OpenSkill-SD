# LoRA Scripts Troubleshooting

## Start Fails Immediately
- Check the latest `screen` log first.
- If the log shows missing Python modules, rerun `scripts/install_lora_scripts.sh` and retry.
- If the log shows missing frontend or tag-editor assets, run `git -C <install-dir> submodule update --init --recursive` and retry.

## Health Check Fails but Process Exists
- Wait and recheck once; first startup may spend extra time loading schemas and GPU checks.
- Verify `curl http://127.0.0.1:<port>/api/presets` on the remote host.
- If `/api/presets` still fails, inspect the latest GUI log for import or CUDA errors.

## Port Conflict
- GUI default port is `28000`; if that port is busy, pick a clean port and restart.
- For `public-port`, keep GUI on `6006` or `6008` and keep tensorboard on `6016` to avoid collisions.

## Tensorboard Issues
- If tensorboard startup is the blocker, try `LORA_SCRIPTS_DISABLE_TENSORBOARD=1` and restart the GUI.
- If tensorboard must stay enabled, move it to a clean internal port with `LORA_SCRIPTS_TENSORBOARD_PORT=<port>`.

## CUDA or Torch Mismatch
- Use the upstream installer through `install.bash --disable-venv` in the system environment.
- If the host image already has incompatible torch packages, rerun the install wrapper and let the upstream installer replace them.
