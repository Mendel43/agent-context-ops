from __future__ import annotations

from pathlib import Path


DEFAULT_CONFIG = """[context]
include = [
  "README.md",
  "AGENTS.md",
  "CLAUDE.md",
  "docs",
]
exclude = [
  ".git",
  ".venv",
  "venv",
  "node_modules",
  "__pycache__",
  "dist",
  "build",
  "private",
  "secrets",
  "graphify-out",
]
max_file_bytes = 20000
max_total_bytes = 180000
"""


DEFAULT_AGENTS = """# Agent Notes

- Keep generated context short and inspectable.
- Do not include secrets, `.env` files or private user data.
- Prefer read-only diagnostics before editing.
"""


def init_project(root: Path, force: bool = False) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    files = {
        root / "agent-context-ops.toml": DEFAULT_CONFIG,
        root / "AGENTS.md": DEFAULT_AGENTS,
        root / "handoffs" / ".gitkeep": "",
        root / "council-runs" / ".gitkeep": "",
    }
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            continue
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written

