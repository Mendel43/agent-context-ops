from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .context_pack import ContextConfig, build_context_pack
from .graph_check import check_graph
from .scan import scan_for_sensitive_content


@dataclass
class DoctorCheck:
    name: str
    status: str
    detail: str

    @property
    def is_failure(self) -> bool:
        return self.status == "FAIL"


def run_doctor(root: Path, config_path: Path | None = None) -> list[DoctorCheck]:
    root = root.resolve()
    checks: list[DoctorCheck] = []

    if not root.exists():
        return [DoctorCheck("Project root", "FAIL", f"path does not exist: {root}")]
    checks.append(DoctorCheck("Project root", "OK", root.name or "."))

    config = config_path or root / "agent-context-ops.toml"
    if config.exists():
        checks.append(DoctorCheck("Config", "OK", config.name))
    else:
        checks.append(DoctorCheck("Config", "WARN", "no config found; using default include/exclude rules"))

    findings = scan_for_sensitive_content(root)
    if findings:
        checks.append(DoctorCheck("Secret scan", "FAIL", f"{len(findings)} sensitive-looking finding(s)"))
    else:
        checks.append(DoctorCheck("Secret scan", "OK", "no sensitive-looking content found"))

    try:
        context_config = ContextConfig.from_file(config if config.exists() else None)
        context = build_context_pack(root, context_config)
    except Exception as exc:  # pragma: no cover - defensive report path
        checks.append(DoctorCheck("Context pack", "FAIL", f"could not build context pack: {exc}"))
    else:
        size = len(context.encode("utf-8"))
        checks.append(DoctorCheck("Context pack", "OK", f"dry run generated {size} bytes"))

    graph_path = root / "graphify-out" / "graph.json"
    graph = check_graph(root, graph_path, (".py", ".md", ".sh", ".json", ".toml"))
    if not graph.exists:
        checks.append(DoctorCheck("Graph freshness", "WARN", "graphify-out/graph.json not found"))
    elif graph.is_fresh:
        checks.append(DoctorCheck("Graph freshness", "OK", "graph is fresh"))
    else:
        checks.append(DoctorCheck("Graph freshness", "WARN", f"{len(graph.changed_files)} changed file(s) after graph build"))

    backup_dir = root / "backups"
    if backup_dir.exists():
        checks.append(DoctorCheck("Backup directory", "OK", str(backup_dir)))
    else:
        checks.append(DoctorCheck("Backup directory", "WARN", "no backups directory found"))

    return checks


def render_doctor_report(checks: list[DoctorCheck]) -> str:
    lines = ["# Agent Context Ops Doctor", ""]
    for check in checks:
        lines.append(f"- `{check.status}` {check.name}: {check.detail}")
    failures = sum(1 for check in checks if check.is_failure)
    warnings = sum(1 for check in checks if check.status == "WARN")
    lines.extend(["", f"Summary: {failures} failure(s), {warnings} warning(s)."])
    return "\n".join(lines) + "\n"
