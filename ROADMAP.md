# Roadmap

## v0.1 - Public skeleton

- Publish README, license, examples and architecture notes. Done.
- Add a safe sample configuration. Done.
- Document what must never be exported. Done.

## v0.1.1 - Public polish

- Add `doctor` command for setup and sharing readiness. Done.
- Add README demo assets. Done.
- Polish quick start and command table. Done.

## v0.1.2 - Compatibility pass

- Add a CLI version flag. Done.
- Test clean editable installs on Windows and Linux. Done.
- Expand CI to Python 3.11 and 3.12. Done.
- Keep examples and release documentation aligned. Done.

## v0.2 - Context pack generator

- Generate a Markdown handoff from configured project paths. Done in first CLI.
- Include recent git status, command references and selected docs. Done in first CLI.
- Redact common secret patterns. Done in first CLI.

## v0.2.0 - Smart context packs

- Add per-agent profiles (`generic`, `codex`, `claude`, `hermes`). Done.
- Embed a machine-readable manifest with a sha256 per file. Done.
- Summarise included files by area. Done.
- Diff a pack against a previous one with `--compare`. Done.

## v0.2.1 - Release hygiene

- Remove unintended co-author metadata from the v0.2.0 release commit. Done.
- Publish a patch release with refreshed package metadata. Done.

## v0.3 - Obsidian logger

- Write reports to an Obsidian-compatible folder structure. Done in first CLI.
- Add daily/session notes.
- Add simple templates for decisions, incidents and handoffs.

## v0.4 - Graph freshness checks

- Detect stale graph outputs. Done in first CLI.
- Report changed files that should be reindexed. Done in first CLI.
- Integrate with Graphify-like generated `graph.json` outputs.

## v0.5 - Agent council logs

- Store read-only review runs from multiple agents. Done in first CLI.
- Keep panel responses and final synthesis as Markdown. Done in first CLI.
- Make reviews auditable without letting secondary agents edit files.

## v0.6 - Hardening

- Add richer redaction patterns.
- Add optional JSON output.
- Add templates for daily notes, incidents and release reviews.
- Add packaged examples with screenshots/GIFs.
