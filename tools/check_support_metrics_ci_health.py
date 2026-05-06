from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import subprocess
import sys

from check_support_metrics_ci_fragments import inspect_fragment_directory


STATE_OK = "ok"
STATE_WARNING = "warning"
STATE_ERROR = "error"
STATE_RANK: dict[str, int] = {STATE_OK: 0, STATE_WARNING: 1, STATE_ERROR: 2}


REQUIRED_TOOLS: tuple[str, ...] = (
    "analyze_run_metrics_history.py",
    "write_support_metrics_ci_summary.py",
    "simulate_support_metrics_ci.py",
    "check_support_metrics_ci_fragments.py",
)
REQUIRED_WORKFLOW_SNIPPETS: tuple[str, ...] = (
    'py -m unittest discover -s tests -p "test_*.py"',
    "py tools/check_support_metrics_ci_fragments.py --validate",
    "py tools/check_support_metrics_ci_health.py --check",
    "artifacts/support_metrics_ci_health.md",
    "support-metrics-ci-health",
    "Get-Content artifacts/support_metrics_ci_health.md | Add-Content -Path $env:GITHUB_STEP_SUMMARY",
    "Smoke test support metrics CI summary (technical fixtures)",
    "Optional runtime support metrics CI check (outputs/ci)",
    "actions/upload-artifact@v4",
    "support-metrics-smoke-report",
    "support-metrics-report",
)
FORBIDDEN_WORKFLOW_SNIPPETS: tuple[str, ...] = ("--fail-on-regression",)
REQUIRED_README_SNIPPETS: tuple[str, ...] = (
    "Support metrics tools index",
    "tools/analyze_run_metrics_history.py",
    "tools/write_support_metrics_ci_summary.py",
    "tools/simulate_support_metrics_ci.py",
    "tools/check_support_metrics_ci_fragments.py",
    "tools/check_support_metrics_ci_health.py",
    "CI/debug only",
    "not gameplay validation",
    "runtime report optional",
    "no --fail-on-regression by default",
)
CLI_HELP_CONTRACT_RELATIVE_PATH = (
    Path("tests") / "fixtures" / "support_metrics_cli_help_expected.json"
)


@dataclass
class ComponentStatus:
    name: str
    state: str
    issues: list[str]
    details: dict[str, object]


@dataclass
class HealthReport:
    tools: ComponentStatus
    fixtures: ComponentStatus
    workflow: ComponentStatus
    fragments: ComponentStatus
    documentation: ComponentStatus
    cli_help: ComponentStatus
    overall: str

    def to_dict(self) -> dict[str, object]:
        return {
            "tools": asdict(self.tools),
            "fixtures": asdict(self.fixtures),
            "workflow": asdict(self.workflow),
            "fragments": asdict(self.fragments),
            "documentation": asdict(self.documentation),
            "cli_help": asdict(self.cli_help),
            "overall": self.overall,
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check global health of support metrics CI tooling, fixtures, "
            "workflow, and fragments contracts."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path (default: current repository root).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when overall health is warning or error.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print health report as JSON.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include per-component issue details in text output.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=None,
        help="Optional path to write a compact Markdown health report.",
    )
    return parser


def _worst_state(states: list[str]) -> str:
    if not states:
        return STATE_OK
    return max(states, key=lambda state: STATE_RANK.get(state, 0))


def _check_tools(root: Path) -> ComponentStatus:
    tools_dir = root / "tools"
    missing: list[str] = []
    present: list[str] = []
    for file_name in REQUIRED_TOOLS:
        path = tools_dir / file_name
        if path.exists():
            present.append(file_name)
        else:
            missing.append(file_name)

    issues: list[str] = []
    state = STATE_OK
    if missing:
        state = STATE_ERROR
        for file_name in missing:
            issues.append("missing tool: tools/%s" % file_name)

    return ComponentStatus(
        name="tools",
        state=state,
        issues=issues,
        details={
            "path": str(tools_dir),
            "present": present,
            "missing": missing,
        },
    )


def _check_fixtures(root: Path) -> ComponentStatus:
    contract_dir = root / "tests" / "fixtures" / "support_metrics_contract"
    fragments_dir = root / "tests" / "fixtures" / "support_metrics_ci_outputs"
    issues: list[str] = []
    state = STATE_OK

    contract_exists = contract_dir.exists()
    fragments_exists = fragments_dir.exists()
    contract_file_count = 0
    fragments_file_count = 0

    if contract_exists:
        contract_file_count = len(list(contract_dir.glob("*.jsonl")))
    if fragments_exists:
        fragments_file_count = len(list(fragments_dir.glob("*.txt")))

    if not contract_exists:
        state = STATE_ERROR
        issues.append("missing fixtures directory: tests/fixtures/support_metrics_contract")
    elif contract_file_count <= 0:
        state = STATE_WARNING
        issues.append("support_metrics_contract has no .jsonl fixtures")

    if not fragments_exists:
        state = STATE_ERROR
        issues.append("missing fixtures directory: tests/fixtures/support_metrics_ci_outputs")
    elif fragments_file_count <= 0 and state != STATE_ERROR:
        state = STATE_WARNING
        issues.append("support_metrics_ci_outputs has no .txt fragments fixtures")

    return ComponentStatus(
        name="fixtures",
        state=state,
        issues=issues,
        details={
            "contract_dir": str(contract_dir),
            "contract_exists": contract_exists,
            "contract_file_count": contract_file_count,
            "fragments_dir": str(fragments_dir),
            "fragments_exists": fragments_exists,
            "fragments_file_count": fragments_file_count,
        },
    )


def _check_workflow(root: Path) -> ComponentStatus:
    workflow_path = root / ".github" / "workflows" / "tests.yml"
    issues: list[str] = []
    state = STATE_OK
    workflow_exists = workflow_path.exists()
    content = ""
    missing_snippets: list[str] = []
    forbidden_found: list[str] = []

    if not workflow_exists:
        state = STATE_ERROR
        issues.append("missing workflow: .github/workflows/tests.yml")
    else:
        content = workflow_path.read_text(encoding="utf-8")
        for snippet in REQUIRED_WORKFLOW_SNIPPETS:
            if snippet not in content:
                missing_snippets.append(snippet)
        for snippet in FORBIDDEN_WORKFLOW_SNIPPETS:
            if snippet in content:
                forbidden_found.append(snippet)

        if missing_snippets:
            state = STATE_ERROR
            for snippet in missing_snippets:
                issues.append("workflow missing snippet: %s" % snippet)
        if forbidden_found and state != STATE_ERROR:
            state = STATE_WARNING
            for snippet in forbidden_found:
                issues.append("workflow contains forbidden snippet: %s" % snippet)

    return ComponentStatus(
        name="workflow",
        state=state,
        issues=issues,
        details={
            "path": str(workflow_path),
            "exists": workflow_exists,
            "missing_required_snippets": missing_snippets,
            "forbidden_snippets_found": forbidden_found,
        },
    )


def _check_fragments(root: Path) -> ComponentStatus:
    fragments_dir = root / "tests" / "fixtures" / "support_metrics_ci_outputs"
    result = inspect_fragment_directory(fragments_dir)
    issues = list(result.issues)
    state = STATE_OK if result.is_valid else STATE_ERROR
    return ComponentStatus(
        name="fragments",
        state=state,
        issues=issues,
        details={
            "path": str(result.directory),
            "missing_files": list(result.missing_files),
            "empty_files": list(result.empty_files),
            "unreadable_files": list(result.unreadable_files),
            "missing_categories": list(result.missing_categories),
        },
    )


def _check_documentation(root: Path) -> ComponentStatus:
    readme_path = root / "README.md"
    issues: list[str] = []
    state = STATE_OK
    readme_exists = readme_path.exists()
    missing_snippets: list[str] = []

    if not readme_exists:
        state = STATE_ERROR
        issues.append("missing documentation file: README.md")
    else:
        content = readme_path.read_text(encoding="utf-8")
        for snippet in REQUIRED_README_SNIPPETS:
            if snippet not in content:
                missing_snippets.append(snippet)
        if missing_snippets:
            state = STATE_ERROR
            for snippet in missing_snippets:
                issues.append("README missing snippet: %s" % snippet)

    return ComponentStatus(
        name="documentation",
        state=state,
        issues=issues,
        details={
            "path": str(readme_path),
            "exists": readme_exists,
            "missing_required_snippets": missing_snippets,
        },
    )


def _check_cli_help(root: Path) -> ComponentStatus:
    fixture_path = root / CLI_HELP_CONTRACT_RELATIVE_PATH
    issues: list[str] = []
    state = STATE_OK
    tools_checked = 0
    tools_with_errors = 0

    if not fixture_path.exists():
        return ComponentStatus(
            name="cli_help",
            state=STATE_ERROR,
            issues=["missing CLI help contract fixture: %s" % str(CLI_HELP_CONTRACT_RELATIVE_PATH)],
            details={
                "fixture_path": str(fixture_path),
                "exists": False,
                "tools_checked": 0,
                "tools_with_errors": 0,
            },
        )

    try:
        parsed = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ComponentStatus(
            name="cli_help",
            state=STATE_ERROR,
            issues=["invalid CLI help contract fixture: %s" % str(exc)],
            details={
                "fixture_path": str(fixture_path),
                "exists": True,
                "tools_checked": 0,
                "tools_with_errors": 0,
            },
        )

    tools = parsed.get("tools")
    if not isinstance(tools, list) or len(tools) == 0:
        return ComponentStatus(
            name="cli_help",
            state=STATE_ERROR,
            issues=["CLI help contract fixture has no tools entries"],
            details={
                "fixture_path": str(fixture_path),
                "exists": True,
                "tools_checked": 0,
                "tools_with_errors": 0,
            },
        )

    for tool_entry in tools:
        if not isinstance(tool_entry, dict):
            tools_with_errors += 1
            issues.append("CLI help fixture entry is not an object")
            continue

        tool_path_raw = str(tool_entry.get("path", "")).strip()
        options = tool_entry.get("options", [])
        if tool_path_raw == "":
            tools_with_errors += 1
            issues.append("CLI help fixture entry missing tool path")
            continue
        if not isinstance(options, list) or len(options) == 0:
            tools_with_errors += 1
            issues.append("CLI help fixture entry has no options: %s" % tool_path_raw)
            continue

        tool_path = root / tool_path_raw
        if not tool_path.exists():
            tools_with_errors += 1
            issues.append("CLI help tool missing: %s" % tool_path_raw)
            continue

        tools_checked += 1
        try:
            help_result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            tools_with_errors += 1
            issues.append("CLI help execution failed for %s: %s" % (tool_path_raw, str(exc)))
            continue

        output = (help_result.stdout or "") + "\n" + (help_result.stderr or "")
        output_lower = output.lower()

        if help_result.returncode != 0:
            tools_with_errors += 1
            issues.append("CLI help returned non-zero for %s: %d" % (tool_path_raw, help_result.returncode))
        if output.strip() == "":
            tools_with_errors += 1
            issues.append("CLI help output is empty for %s" % tool_path_raw)
        if "traceback" in output_lower:
            tools_with_errors += 1
            issues.append("CLI help output contains traceback for %s" % tool_path_raw)
        if ("usage" not in output_lower) and ("options" not in output_lower):
            tools_with_errors += 1
            issues.append("CLI help output missing usage/options for %s" % tool_path_raw)
        for option in options:
            if str(option) not in output:
                tools_with_errors += 1
                issues.append("CLI help missing option %s for %s" % (str(option), tool_path_raw))

    if issues:
        state = STATE_ERROR

    return ComponentStatus(
        name="cli_help",
        state=state,
        issues=issues,
        details={
            "fixture_path": str(fixture_path),
            "exists": True,
            "tools_checked": tools_checked,
            "tools_with_errors": tools_with_errors,
        },
    )


def build_health_report(root: Path) -> HealthReport:
    tools = _check_tools(root)
    fixtures = _check_fixtures(root)
    workflow = _check_workflow(root)
    fragments = _check_fragments(root)
    documentation = _check_documentation(root)
    cli_help = _check_cli_help(root)
    overall = _worst_state(
        [
            tools.state,
            fixtures.state,
            workflow.state,
            fragments.state,
            documentation.state,
            cli_help.state,
        ]
    )
    return HealthReport(
        tools=tools,
        fixtures=fixtures,
        workflow=workflow,
        fragments=fragments,
        documentation=documentation,
        cli_help=cli_help,
        overall=overall,
    )


def _print_text_report(report: HealthReport, verbose: bool) -> None:
    print("Support metrics CI health:")
    print("- tools: %s" % report.tools.state)
    print("- fixtures: %s" % report.fixtures.state)
    print("- workflow: %s" % report.workflow.state)
    print("- fragments: %s" % report.fragments.state)
    print("- documentation: %s" % report.documentation.state)
    print("- cli_help: %s" % report.cli_help.state)
    print("- overall: %s" % report.overall)

    if not verbose:
        return

    for component in (
        report.tools,
        report.fixtures,
        report.workflow,
        report.fragments,
        report.documentation,
        report.cli_help,
    ):
        print("")
        print("%s details:" % component.name)
        if component.issues:
            for issue in component.issues:
                print("- %s" % issue)
        else:
            print("- no issues")


def _build_markdown_report(report: HealthReport) -> str:
    lines: list[str] = []
    lines.append("# Support metrics CI health")
    lines.append("")
    lines.append("- overall: %s" % report.overall)
    lines.append("- tools: %s" % report.tools.state)
    lines.append("- fixtures: %s" % report.fixtures.state)
    lines.append("- fragments: %s" % report.fragments.state)
    lines.append("- workflow: %s" % report.workflow.state)
    lines.append("- documentation: %s" % report.documentation.state)
    lines.append("- cli_help: %s" % report.cli_help.state)
    lines.append("- cli_help contract: support metrics tools --help")
    lines.append(
        "- interpretation: maintenance CI/debug only, not gameplay validation"
    )
    return "\n".join(lines) + "\n"


def _write_markdown_report(path: Path, report: HealthReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_build_markdown_report(report), encoding="utf-8")


def main() -> int:
    args = _build_parser().parse_args()
    report = build_health_report(args.root)

    if args.markdown_output is not None:
        _write_markdown_report(args.markdown_output, report)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report, verbose=bool(args.verbose))

    if args.check and report.overall != STATE_OK:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
