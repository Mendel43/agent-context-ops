from pathlib import Path

from agent_context_ops.scan import scan_for_sensitive_content


def test_scan_finds_env_file(tmp_path: Path):
    key = "TO" + "KEN"
    (tmp_path / ".env").write_text(f"{key}=abc\n", encoding="utf-8")
    findings = scan_for_sensitive_content(tmp_path)
    assert findings
