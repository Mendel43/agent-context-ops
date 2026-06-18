# Agent Context Ops v0.1.2

v0.1.2 is a small compatibility and release-quality update.

## Highlights

- Added `agent-context-ops --version` and `aco --version`.
- Expanded CI to Windows and Linux with Python 3.11 and 3.12.
- Made the smoke-test workflow portable across supported platforms.
- Added a regression test that keeps the CLI and package version aligned.

## Upgrade

From a local checkout:

```bash
git pull
python -m pip install -e .
agent-context-ops --version
```

Expected output:

```text
agent-context-ops 0.1.2
```
