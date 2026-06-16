# Agent Instructions

This repository is intended to be public open source.

## Safety

- Do not commit secrets, `.env` files, private business data or user-specific paths.
- Keep examples generic.
- Commands should be read-only by default.
- Any command that writes files must require an explicit destination argument.
- Prefer small, inspectable Markdown outputs.

## Project shape

- Python package: `src/agent_context_ops`
- CLI entry point: `agent-context-ops`
- Tests: `tests`
- Docs: `docs`

## Verification

Run:

```bash
PYTHONPATH=src python3 -m compileall -q src tests
PYTHONPATH=src python3 -m agent_context_ops.cli --help
```

If `pytest` is installed:

```bash
PYTHONPATH=src pytest -q
```

