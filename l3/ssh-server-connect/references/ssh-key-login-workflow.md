# SSH Key Login Workflow

## First-Time Onboarding
1. Decide login mode and record it in local markdown state files.
   Update `state.md` and `login/method.md` with `key` or `password`.
2. If `LOGIN_METHOD=key`, create local key pair if absent.
3. If platform supports SSH key management (for example AutoDL), upload public key in platform settings first.
4. If platform key import is unavailable, push local public key using one-time password login.
5. Test `BatchMode` key login.
6. Add host alias to local SSH config.

## Password Mode (Supported)
Use when credentials are dynamic and key mode is not configured yet.

Core commands:
```bash
ssh -p <port> <user>@<host> '<command>'
scp -P <port> <local_path> <user>@<host>:<remote_path>
```

Do not store plaintext password in skill files.

## Key Mode (Supported)
Recommended for repeated automation and stable operations.

### AutoDL Preferred Pattern
1. Create local key pair if absent.
2. If platform supports SSH key management (for example AutoDL), upload public key in platform settings first.
3. If platform key import is unavailable, push local public key using one-time password login.
4. Test `BatchMode` key login.
5. Add host alias to local SSH config.

## Recommended SSH Config Entry
```sshconfig
Host autodl-westc-01
  HostName <your-autodl-host>
  Port 19992
  User root
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

## Verification Command
```bash
ssh -o BatchMode=yes -p <port> <user>@<host> 'echo key-login-ok'
```

## Markdown Update Command
```bash
python scripts/record_login_state.py <workspace-root> <server-alias> <key|password> [identity-file] [ssh-alias]
```
