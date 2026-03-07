# AutoDL Port Mapping

## Goal
Expose remote ComfyUI service to a local/browser-accessible URL on AutoDL.

## Default Port Policy
- `public-port`: run ComfyUI directly on AutoDL service port `6006`; if unavailable, use `6008`.
- `ssh-tunnel-cli`: keep ComfyUI on internal port `8188`.
- `ssh-tunnel-gui`: keep ComfyUI on internal port `8188` unless AutoDL client tooling requires a different forwarded local port.

## Requirements
1. Confirm the access mode with the user before starting the service.
2. If `public-port` is selected, ComfyUI must listen on the chosen AutoDL service port (`6006` or `6008`).
3. If `ssh-tunnel-cli` or `ssh-tunnel-gui` is selected, ComfyUI should listen on `0.0.0.0:8188` in the container.
4. Public custom service mode may require enterprise real-name verification based on platform policy.

## Steps
1. Choose mode:
   - `public-port` (AutoDL custom service mapped public URL; default `6006`, fallback `6008`)
   - `ssh-tunnel-cli` (command tunnel)
   - `ssh-tunnel-gui` (official client software tunnel)
2. Start ComfyUI service:
```bash
scripts/comfyui_screen_ctl.sh start /root/autodl-tmp/comfyui/app comfyui-main
```
3. For `public-port`, run on service port `6006` or `6008`:
```bash
COMFYUI_PORT=6006 scripts/comfyui_screen_ctl.sh start /root/autodl-tmp/comfyui/app comfyui-main
```
4. In AutoDL panel, create or enable mapping for the chosen public service port.
   If custom service is unavailable for current account type, switch to SSH proxy mode.
5. For `ssh-tunnel-cli`, use:
```bash
ssh -CN -L 8188:127.0.0.1:8188 -p <ssh-port> <user>@<host>
```
6. Open mapped URL or local tunnel URL.
7. Verify API health after service start:
```bash
scripts/comfyui_healthcheck.sh 127.0.0.1 <6006|6008|8188>
```

## Notes
- Mapping method depends on AutoDL official tooling and docs.
- Keep `screen` session alive; if session stops, mapped URL will become unavailable.
- Public mapped services are subject to platform policy and legal/regulatory oversight.
- Do not use public endpoints for illegal, abusive, or non-compliant distribution scenarios.
