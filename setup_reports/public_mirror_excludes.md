# Public Mirror Excludes

- generated_at_utc: 2026-03-14T10:51:56.6836463Z
- source: setup_reports/public_mirror_excludes.txt

## Exclude Rules

```text
*.key
*.p12
*.pem
*.pfx
.env
.env.*
.git/
.venv/
__pycache__/
credentials*
id_ed25519
id_rsa
projects/wild_hunt_command_citadel/shortform_core/
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/certifi/cacert.pem
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/pip/_vendor/certifi/cacert.pem
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/pip/_vendor/pygments/__pycache__/token.cpython-312.pyc
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/pip/_vendor/pygments/token.py
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/pygments/__pycache__/token.cpython-312.pyc
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/pygments/token.py
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/PySide6/scripts/qtpy2cpp_lib/__pycache__/tokenizer.cpython-312.pyc
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/PySide6/scripts/qtpy2cpp_lib/tokenizer.py
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/yaml/__pycache__/tokens.cpython-312.pyc
projects/wild_hunt_command_citadel/shortform_core/.venv/Lib/site-packages/yaml/tokens.py
projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/.venv/Lib/site-packages/pip/_vendor/certifi/cacert.pem
projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/.venv/Lib/site-packages/pip/_vendor/pygments/__pycache__/token.cpython-312.pyc
projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/.venv/Lib/site-packages/pip/_vendor/pygments/token.py
projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/.venv/Lib/site-packages/PySide6/scripts/qtpy2cpp_lib/__pycache__/tokenizer.cpython-312.pyc
projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/.venv/Lib/site-packages/PySide6/scripts/qtpy2cpp_lib/tokenizer.py
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/certifi/cacert.pem
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/pip/_vendor/certifi/cacert.pem
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/pip/_vendor/pygments/__pycache__/token.cpython-312.pyc
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/pip/_vendor/pygments/token.py
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/pygments/__pycache__/token.cpython-312.pyc
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/pygments/token.py
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/PySide6/scripts/qtpy2cpp_lib/__pycache__/tokenizer.cpython-312.pyc
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/PySide6/scripts/qtpy2cpp_lib/tokenizer.py
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/yaml/__pycache__/tokens.cpython-312.pyc
projects/wild_hunt_command_citadel/tiktok_agent_platform/core/.venv/Lib/site-packages/yaml/tokens.py
secrets.*
token*
venv/
```

## Policy

- source repo is the only source of truth
- mirror is one-way sync from source repo
- excluded paths are never published
- .git, env files, private keys, token/credential-like files are excluded
- local legacy residue path shortform_core is excluded from public mirror
- local virtual environments/cache folders are excluded to avoid publishing machine-local binaries
