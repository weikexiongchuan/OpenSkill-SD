# ComfyUI Troubleshooting

## Service Not Reachable
1. Check session exists: `scripts/comfyui_screen_ctl.sh status <session>`.
2. Check local API: `scripts/comfyui_healthcheck.sh 127.0.0.1 <port>`.
3. Check launch log under `<install-dir>/logs/`.

## CUDA or Torch Errors
1. Confirm `nvidia-smi` works on server.
2. Confirm system Python environment has compatible torch build.
3. Reinstall dependencies in system environment if binary mismatch appears.

## Port Collision
- Change port and restart:
```bash
scripts/comfyui_screen_ctl.sh stop <session>
COMFYUI_PORT=<new-port> scripts/comfyui_screen_ctl.sh start <install-dir> <session>
```

## Large Model Load Delays
- Keep models on fast storage volume.
- Avoid loading from temporary or network-mounted paths where possible.
