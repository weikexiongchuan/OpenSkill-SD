# SSH Hardening Checklist

## Pre-Checks
1. Confirm key login works from at least two terminals.
2. Confirm provider console access exists in case of lockout.
3. Back up `/etc/ssh/sshd_config` before edits.

## Recommended Baseline
- `PubkeyAuthentication yes`
- `PasswordAuthentication no`
- `ChallengeResponseAuthentication no`
- `KbdInteractiveAuthentication no`
- `PermitRootLogin prohibit-password`

## Rollout Strategy
1. Run dry-run script to preview changes.
2. Apply changes during a maintenance window.
3. Keep active session open while restarting SSH service.
4. Re-test key login after restart.
