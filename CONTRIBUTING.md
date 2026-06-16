# Contributing

Contributions are welcome.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
agent-context-ops --help
```

## Principles

- Keep commands read-only by default.
- Do not add provider-specific lock-in unless it is optional.
- Prefer Markdown outputs that humans can inspect.
- Add tests for redaction, path safety and report generation.
- Never commit secrets or private project assumptions.

