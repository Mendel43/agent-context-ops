from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re

from .redact import redact_text


def write_council_log(
    output_dir: Path,
    question: str,
    panels: list[tuple[str, str]],
    final: str | None,
) -> Path:
    """Write a read-only multi-agent review transcript."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "created_at": datetime.now().isoformat(),
        "question": question,
        "panels": [name for name, _ in panels],
        "has_final": final is not None,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (run_dir / "question.md").write_text(f"# Question\n\n{redact_text(question).rstrip()}\n", encoding="utf-8")

    for name, body in panels:
        safe_name = _safe_filename(name)
        (run_dir / f"panel_{safe_name}.md").write_text(
            f"# Panel: {name}\n\n{redact_text(body).rstrip()}\n",
            encoding="utf-8",
        )

    if final is not None:
        (run_dir / "final.md").write_text(f"# Final\n\n{redact_text(final).rstrip()}\n", encoding="utf-8")

    return run_dir


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return value or "agent"

