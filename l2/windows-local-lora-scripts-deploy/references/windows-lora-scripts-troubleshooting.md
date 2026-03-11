# Windows Local LoRA Scripts Troubleshooting

## Common Checks
- Confirm the selected conda env is Python `3.10`.
- Confirm `torch.cuda.is_available() == True`.
- Confirm `frontend/dist` and `mikazuki/dataset-tag-editor/scripts` both exist.
- If GUI start-up fails, inspect `<workspace-root>/lora-scripts.log`.
- If TensorBoard fails separately, verify port `6006` is free before retrying.

## First Recovery Moves
1. Re-run the Python version and CUDA Torch checks.
2. Reinstall `xformers`.
3. Re-run `pip install --upgrade -r requirements.txt`.
4. Repair the two submodules if either path is missing.
5. Restart the GUI on `127.0.0.1:28000`.
