# Release Notes - v0.1.1

`v0.1.1` is a polish release for the first public version of Agent Context Ops.

## Highlights

- Added `agent-context-ops doctor`, a local preflight check before sharing context
  with another AI coding agent.
- Improved the README with clearer use cases, quick start steps and command table.
- Added demo assets for the README.
- Expanded CLI docs and the release checklist.
- Context packs now hide absolute local root paths by default.

## Why it matters

The project is meant to make AI-assisted maintenance safer and less messy. This
release makes the first-run experience clearer: users can initialize a project,
run a doctor check, generate a handoff, scan for secrets and verify local graph
freshness from one small CLI.

## Verification

Before publishing this release, run:

```bash
make smoke
pytest -q
agent-context-ops doctor --root .
agent-context-ops scan-secrets --root .
```
