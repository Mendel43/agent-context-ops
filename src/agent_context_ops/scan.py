from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .fs_safety import DEFAULT_EXCLUDES, is_sensitive_path, should_skip
from .redact import SECRET_PATTERNS


@dataclass
class ScanFinding:
    path: Path
    line: int | None
    kind: str


def scan_for_sensitive_content(root: Path) -> list[ScanFinding]:
    root = root.resolve()
    findings: list[ScanFinding] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path, root, set(DEFAULT_EXCLUDES)):
            continue
        if is_sensitive_path(path):
            findings.append(ScanFinding(path, None, "sensitive filename"))
            continue
        if path.suffix.lower() not in {".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".py", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            if "allow-secret" in line:
                continue
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                findings.append(ScanFinding(path, idx, "secret-like text"))
    return findings


def render_scan_report(root: Path, findings: list[ScanFinding]) -> str:
    lines = ["# Sensitive Content Scan", ""]
    lines.append(f"- Findings: `{len(findings)}`")
    for finding in findings:
        rel = finding.path.relative_to(root.resolve())
        line = "" if finding.line is None else f":{finding.line}"
        lines.append(f"- `{finding.kind}` `{rel}{line}`")
    return "\n".join(lines) + "\n"
