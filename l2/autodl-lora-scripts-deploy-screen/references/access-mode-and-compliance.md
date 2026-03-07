# Access Mode and Compliance

## Deployment-Time Required Confirmation
When user asks to deploy services, confirm the access choice first, but explain it in user-facing Chinese instead of raw terms. Ask the user to choose exactly one meaning:
1. `直接给我一个浏览器网址` → internal mapping: `public-port`
2. `只在我这台电脑里打开` → internal mapping: `ssh-tunnel-cli`
3. `走 AutoDL 官方客户端转发` → internal mapping: `ssh-tunnel-gui`

Do not skip this confirmation, but do not force the user to repeat the internal term names.
Keep the user-facing confirmation brief: prefer `1` sentence, keep it under about `60` Chinese characters, and use a second sentence only when the difference must be clarified.

## Mode Guidance
- `直接给我一个浏览器网址` / `public-port`: fastest direct browser access, but exposed endpoint risk is higher. Platform policy may require enterprise real-name verification for custom public service.
- `只在我这台电脑里打开` / `ssh-tunnel-cli`: no extra software, local-only forwarding, usually the best default for private use.
- `走 AutoDL 官方客户端转发` / `ssh-tunnel-gui`: easier for users who prefer official GUI tools.

## Suggested Confirmation Prompt
Use one short confirmation before execution:

"你想怎么打开：1 直接给网址；2 只在这台电脑打开（推荐）；3 走 AutoDL 客户端？"

Optional second sentence when clarification is needed:

"1 最省事但会公网暴露；2 更安全；3 适合习惯官方工具。"

## Compliance Notice Template
Use this wording when `public-port` is selected:

"公网端口可能被平台或监管审计，请仅用于合规学术/研究用途，不用于违法、滥用或违规分发场景。"

## Final Response Rule
After the service is reachable, open the final URL in the local browser by default without asking the user again. Then return the final service URL plus one fixed short support sentence: "如果服务不可用请告诉我，我将为您排查问题。" If the browser-open step failed, add at most one additional short fallback sentence.

## Command Baselines
### public-port
```bash
LORA_SCRIPTS_PORT=6006 LORA_SCRIPTS_TENSORBOARD_PORT=6016 scripts/lora_scripts_screen_ctl.sh start /root/autodl-tmp/lora-scripts/app lora-scripts-main
```

### ssh-tunnel-cli
```bash
ssh -CN -L 28000:127.0.0.1:28000 -p <ssh-port> <user>@<host>
```

### ssh-tunnel-gui
Follow official AutoDL proxy/client documentation for local port forwarding.
