from pathlib import Path

from agent_context_ops.doctor import render_doctor_report, run_doctor


def test_doctor_warns_but_passes_for_minimal_project(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    checks = run_doctor(tmp_path)
    report = render_doctor_report(checks)
    assert "`OK` Project root" in report
    assert "`OK` Context pack" in report
    assert "`WARN` Config" in report
    assert not any(check.is_failure for check in checks)


def test_doctor_fails_on_sensitive_content(tmp_path: Path):
    key = "TO" + "KEN"
    (tmp_path / "README.md").write_text(f"{key}=secretsecretsecretsecret\n", encoding="utf-8")  # allow-secret
    checks = run_doctor(tmp_path)
    assert any(check.name == "Secret scan" and check.is_failure for check in checks)
