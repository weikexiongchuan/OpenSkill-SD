# Windows Local ComfyUI Troubleshooting

## Common Checks
- Confirm the selected conda env reports `torch.cuda.is_available() == True`.
- Confirm the port is not already occupied.
- If the browser opens but workflow execution fails, inspect `<workspace-root>/comfyui.log`.
- If Torch is CPU-only, reinstall the GPU wheel set before retrying ComfyUI.

## First Recovery Moves
1. Re-run the Torch CUDA check inside the selected env.
2. Re-run `pip install -r requirements.txt`.
3. Restart ComfyUI with the same host and port.
4. If `8188` is occupied, move to the next free local port and repeat the health check.
