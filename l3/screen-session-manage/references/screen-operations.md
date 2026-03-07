# Screen Operations

## Rule
Treat screen as mandatory process supervisor for long-running tasks.

## Start Policy
- Always assign explicit session name.
- Always enable persistent log output.
- Always write launch metadata to file before starting.

## Session Lifecycle
1. Start: `scripts/screen_session_ctl.sh start <session> <log-file> -- <command...>`
2. Check: `scripts/screen_session_ctl.sh status <session>`
3. Attach: `scripts/screen_session_ctl.sh attach <session>`
4. Stop: `scripts/screen_session_ctl.sh stop <session>`

## Failure Recovery
- If session exits, inspect last log lines first.
- Relaunch using the same run metadata and command file.
- Do not start a second conflicting session with the same run name.
