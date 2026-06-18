# Release Checklist

- Run compile checks.
- Run tests.
- Verify `agent-context-ops --version` matches `pyproject.toml` and the release tag.
- Confirm the Windows and Linux CI matrix passes.
- Run `agent-context-ops doctor --root .`.
- Generate a sample context pack.
- Confirm `.env` and private files are not exported.
- Confirm README examples still work.
- Regenerate demo screenshot/GIF when CLI output changes.
- Update `ROADMAP.md`.
- Tag the release.
