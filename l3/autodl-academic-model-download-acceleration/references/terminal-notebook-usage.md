# Terminal and Notebook Usage

## Terminal Enable
```bash
source /etc/network_turbo
```

## Notebook Enable
```python
import subprocess
import os

result = subprocess.run('bash -c "source /etc/network_turbo && env | grep proxy"', shell=True, capture_output=True, text=True)
output = result.stdout
for line in output.splitlines():
    if '=' in line:
        var, value = line.split('=', 1)
        os.environ[var] = value
```

## Disable Acceleration
If acceleration is no longer needed, disable proxy variables.

Minimum:
```bash
unset http_proxy && unset https_proxy
```

Recommended full cleanup:
```bash
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy NO_PROXY
```
