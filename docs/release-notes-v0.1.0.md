# Agent Context Ops v0.1.0

This is the first public release of Agent Context Ops.

## Highlights

- Generate redacted Markdown handoffs for AI coding agents.
- Write operational notes to Obsidian-compatible vaults.
- Check backup freshness for critical files.
- Check whether a local knowledge graph output is stale.
- Scan for secret-looking content before sharing context.
- Record read-only multi-agent review logs.

## Safety

- `.env` and common secret files are skipped.
- Redaction is best-effort and documented.
- Commands are read-only by default unless an explicit output destination is provided.
- CI and smoke tests are enabled.

## Install

```bash
pip install -e .
```

## Try it

```bash
agent-context-ops context-pack --root . --output handoff.md
agent-context-ops scan-secrets --root .
```

