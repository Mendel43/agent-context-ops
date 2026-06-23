# Agent Context Ops v0.2.0

v0.2.0 turns `context-pack` into a smart, agent-aware handoff generator.

## Highlights

- **Profiles.** Choose `--profile generic|codex|claude|hermes`. Each profile picks
  a tailored include set and byte budget so the pack fits how that agent consumes
  context. `codex` ships code (`src/`, `tests/`); `hermes` stays lean.
- **Manifest.** Every pack embeds a machine-readable JSON manifest: profile, file
  count, total bytes, and a sha256 per included file.
- **Area summary.** A `## Areas` table groups included files by top-level
  directory so a reviewer sees the shape of the pack at a glance.
- **Diffing.** `--compare previous-pack.md` adds a `## Changes since previous
  pack` section listing added, removed and changed files.

## Upgrade

From a local checkout:

```bash
git pull
python -m pip install -e .
agent-context-ops --version
```

Expected output:

```text
agent-context-ops 0.2.0
```

## Try it

```bash
agent-context-ops context-pack --root . --profile codex --output handoff.md
agent-context-ops context-pack --root . --profile codex \
  --compare handoff.md --output handoff-next.md
```
