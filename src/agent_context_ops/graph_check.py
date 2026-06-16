from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .fs_safety import DEFAULT_EXCLUDES, should_skip


@dataclass
class GraphStatus:
    graph_path: Path
    exists: bool
    changed_files: list[Path]

    @property
    def is_fresh(self) -> bool:
        return self.exists and not self.changed_files


def check_graph(root: Path, graph_path: Path, suffixes: tuple[str, ...]) -> GraphStatus:
    root = root.resolve()
    graph_path = graph_path.resolve()
    if not graph_path.exists():
        return GraphStatus(graph_path, False, [])
    graph_mtime = graph_path.stat().st_mtime
    changed: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path, root, set(DEFAULT_EXCLUDES)):
            continue
        if path.resolve() == graph_path:
            continue
        if path.suffix.lower() in suffixes and path.stat().st_mtime > graph_mtime:
            changed.append(path)
    return GraphStatus(graph_path, True, sorted(changed))


def render_graph_report(status: GraphStatus, root: Path, limit: int = 50) -> str:
    lines = ["# Graph Freshness Check", ""]
    if not status.exists:
        lines.append(f"- `FAIL` graph file not found: `{status.graph_path}`")
        return "\n".join(lines) + "\n"
    lines.append(f"- Graph: `{status.graph_path}`")
    lines.append(f"- Fresh: `{status.is_fresh}`")
    lines.append(f"- Changed files: `{len(status.changed_files)}`")
    for path in status.changed_files[:limit]:
        lines.append(f"  - `{path.relative_to(root.resolve())}`")
    if len(status.changed_files) > limit:
        lines.append(f"  - ... {len(status.changed_files) - limit} more")
    return "\n".join(lines) + "\n"

