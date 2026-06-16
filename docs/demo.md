# Demo

Generate a handoff:

```bash
agent-context-ops context-pack --root . --output handoff.md
```

Example output shape:

````markdown
# Agent Context Pack

- Generated: `2026-06-15T20:00:00+00:00`
- Root: `/repo`

## Git

```text
clean
```

## Files

### `README.md`

...
````

Check graph freshness:

```bash
agent-context-ops graph-check --root . --graph graphify-out/graph.json
```

Write an Obsidian note:

```bash
echo "Reviewed release blockers." | agent-context-ops obsidian-log \
  --vault ~/Notes \
  --folder "Maintenance" \
  --title "Release Review"
```
