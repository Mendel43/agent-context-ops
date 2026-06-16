from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .backup_check import check_backups, render_backup_report
from .context_pack import ContextConfig, build_context_pack
from .council_log import write_council_log
from .doctor import render_doctor_report, run_doctor
from .graph_check import check_graph, render_graph_report
from .init_project import init_project
from .obsidian_log import write_obsidian_note
from .scan import render_scan_report, scan_for_sensitive_content


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-context-ops")
    parser.add_argument("--root", default=".", help="Project root")
    sub = parser.add_subparsers(dest="command", required=True)

    context = sub.add_parser("context-pack", help="Generate a redacted Markdown handoff")
    context.add_argument("--root", default=argparse.SUPPRESS, help="Project root")
    context.add_argument("--config", help="Optional TOML config")
    context.add_argument("--output", help="Write to file instead of stdout")
    context.add_argument("--include", action="append", help="Extra include path, relative to root")
    context.add_argument("--show-root-path", action="store_true", help="Include the absolute root path in output")
    context.set_defaults(func=cmd_context_pack)

    backup = sub.add_parser("backup-check", help="Check whether critical files have recent backups")
    backup.add_argument("--root", default=argparse.SUPPRESS, help="Project root")
    backup.add_argument("--file", action="append", required=True, help="Critical file, relative to root")
    backup.add_argument("--backup-dir", default="backups", help="Backup directory")
    backup.add_argument("--max-age-days", type=int, default=7)
    backup.add_argument("--output", help="Write report to file")
    backup.set_defaults(func=cmd_backup_check)

    graph = sub.add_parser("graph-check", help="Check whether graph output is stale")
    graph.add_argument("--root", default=argparse.SUPPRESS, help="Project root")
    graph.add_argument("--graph", default="graphify-out/graph.json")
    graph.add_argument("--suffix", action="append", default=[".py", ".md", ".sh", ".json", ".toml"])
    graph.add_argument("--output", help="Write report to file")
    graph.set_defaults(func=cmd_graph_check)

    obsidian = sub.add_parser("obsidian-log", help="Write a Markdown note to an Obsidian vault")
    obsidian.add_argument("--vault", required=True)
    obsidian.add_argument("--folder", default="AI Logs")
    obsidian.add_argument("--title", required=True)
    obsidian.add_argument("--body", help="Body text. If omitted, stdin is used.")
    obsidian.set_defaults(func=cmd_obsidian_log)

    init = sub.add_parser("init", help="Create a minimal agent context structure")
    init.add_argument("--root", default=argparse.SUPPRESS, help="Project root")
    init.add_argument("--force", action="store_true", help="Overwrite generated files")
    init.set_defaults(func=cmd_init)

    scan = sub.add_parser("scan-secrets", help="Scan exported context for secret-looking content")
    scan.add_argument("--root", default=argparse.SUPPRESS, help="Project root")
    scan.add_argument("--output", help="Write report to file")
    scan.set_defaults(func=cmd_scan_secrets)

    doctor = sub.add_parser("doctor", help="Run a local readiness check before sharing context")
    doctor.add_argument("--root", default=argparse.SUPPRESS, help="Project root")
    doctor.add_argument("--config", help="Optional TOML config")
    doctor.add_argument("--output", help="Write report to file")
    doctor.set_defaults(func=cmd_doctor)

    council = sub.add_parser("council-log", help="Record a read-only multi-agent review")
    council.add_argument("--output-dir", default="council-runs")
    council.add_argument("--question", required=True)
    council.add_argument(
        "--panel",
        action="append",
        default=[],
        help="Panel response as name=path. May be repeated.",
    )
    council.add_argument("--final", help="Final synthesis file")
    council.set_defaults(func=cmd_council_log)

    return parser


def cmd_context_pack(args: argparse.Namespace) -> int:
    root = Path(args.root)
    config = ContextConfig.from_file(Path(args.config) if args.config else None)
    if args.include:
        config.include.extend(args.include)
    if args.show_root_path:
        config.show_absolute_root = True
    output = build_context_pack(root, config)
    _emit(output, args.output)
    return 0


def cmd_backup_check(args: argparse.Namespace) -> int:
    root = Path(args.root)
    findings = check_backups(root, args.file, root / args.backup_dir, args.max_age_days)
    output = render_backup_report(findings)
    _emit(output, args.output)
    return 0 if all(finding.ok for finding in findings) else 2


def cmd_graph_check(args: argparse.Namespace) -> int:
    root = Path(args.root)
    status = check_graph(root, root / args.graph, tuple(args.suffix))
    output = render_graph_report(status, root)
    _emit(output, args.output)
    return 0 if status.is_fresh else 2


def cmd_obsidian_log(args: argparse.Namespace) -> int:
    body = args.body if args.body is not None else sys.stdin.read()
    path = write_obsidian_note(Path(args.vault), args.folder, args.title, body)
    print(path)
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    written = init_project(Path(args.root), force=args.force)
    for path in written:
        print(path)
    return 0


def cmd_scan_secrets(args: argparse.Namespace) -> int:
    root = Path(args.root)
    findings = scan_for_sensitive_content(root)
    output = render_scan_report(root, findings)
    _emit(output, args.output)
    return 0 if not findings else 2


def cmd_doctor(args: argparse.Namespace) -> int:
    checks = run_doctor(Path(args.root), Path(args.config) if args.config else None)
    output = render_doctor_report(checks)
    _emit(output, args.output)
    return 2 if any(check.is_failure for check in checks) else 0


def cmd_council_log(args: argparse.Namespace) -> int:
    root = Path(args.root)
    panels: list[tuple[str, str]] = []
    for item in args.panel:
        if "=" not in item:
            raise SystemExit("--panel must use name=path")
        name, path_text = item.split("=", 1)
        panels.append((name, Path(path_text).read_text(encoding="utf-8")))
    final = Path(args.final).read_text(encoding="utf-8") if args.final else None
    run_dir = write_council_log(root / args.output_dir, args.question, panels, final)
    print(run_dir)
    return 0


def _emit(output: str, path: str | None) -> None:
    if path:
        Path(path).write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    raise SystemExit(main())
