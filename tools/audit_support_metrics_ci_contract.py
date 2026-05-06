from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from check_support_metrics_ci_fragments import (
    EXPECTED_CATEGORIES,
    inspect_fragment_directory,
)


STATE_OK = "ok"
STATE_ERROR = "error"
STATE_RANK: dict[str, int] = {STATE_OK: 0, STATE_ERROR: 1}

REQUIRED_WORKFLOW_STEP_SNIPPETS: tuple[str, ...] = (
    "Run unit tests",
    "Validate support metrics CI fragments",
    "Validate support metrics CI health",
    "Smoke test support metrics CI summary",
    "Optional runtime support metrics CI check",
)
REQUIRED_ARTIFACT_NAMES: tuple[str, ...] = (
    "support-metrics-smoke-report",
    "support-metrics-report",
    "support-metrics-ci-health",
    "support-metrics-ci-contract-audit",
)
REQUIRED_FRAGMENT_CATEGORIES: tuple[str, ...] = (
    "smoke",
    "runtime",
    "error",
    "local",
    "health",
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
class ContractAuditReport:
    cli_readme_tools: ComponentStatus
    artifacts_alignment: ComponentStatus
    fragments_coverage: ComponentStatus
    workflow_rules: ComponentStatus
    tool_scripts: ComponentStatus
    overall: str

    def to_dict(self) -> dict[str, object]:
        return {
            "cli_readme_tools": asdict(self.cli_readme_tools),
            "artifacts_alignment": asdict(self.artifacts_alignment),
            "fragments_coverage": asdict(self.fragments_coverage),
            "workflow_rules": asdict(self.workflow_rules),
            "tool_scripts": asdict(self.tool_scripts),
            "overall": self.overall,
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit support metrics CI contract coherence between README, workflow, "
            "fixtures, fragments and maintenance tools."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path (default: current repository root).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the audit report as JSON.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when at least one incoherence is found.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed issues for each component in text mode.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=None,
        help="Optional path to write a compact Markdown contract audit report.",
    )
    return parser


def _worst_state(states: list[str]) -> str:
    if not states:
        return STATE_OK
    return max(states, key=lambda state: STATE_RANK.get(state, 0))


def _extract_step_block(workflow_content: str, step_label_prefix: str) -> str:
    marker = "- name: %s" % step_label_prefix
    start = workflow_content.find(marker)
    if start < 0:
        return ""
    next_start = workflow_content.find("\n      - name:", start + len(marker))
    if next_start < 0:
        return workflow_content[start:]
    return workflow_content[start:next_start]


def _load_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), ""
    except OSError as exc:
        return "", str(exc)


def _load_cli_help_tools(fixture_path: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    if not fixture_path.exists():
        return [], ["missing CLI help fixture: %s" % str(fixture_path)]

    try:
        parsed = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], ["invalid CLI help fixture: %s" % str(exc)]

    tools = parsed.get("tools")
    if not isinstance(tools, list) or len(tools) == 0:
        return [], ["CLI help fixture has no tools entries"]

    paths: list[str] = []
    for tool_entry in tools:
        if not isinstance(tool_entry, dict):
            issues.append("CLI help fixture entry is not an object")
            continue
        path_value = str(tool_entry.get("path", "")).strip()
        if path_value == "":
            issues.append("CLI help fixture entry missing tool path")
            continue
        paths.append(path_value)

    return paths, issues


def _check_cli_readme_tools(root: Path, readme_content: str) -> ComponentStatus:
    issues: list[str] = []
    fixture_path = root / CLI_HELP_CONTRACT_RELATIVE_PATH
    cli_tool_paths, fixture_issues = _load_cli_help_tools(fixture_path)
    issues.extend(fixture_issues)

    for tool_path in cli_tool_paths:
        if tool_path not in readme_content:
            issues.append("README missing CLI fixture tool mention: %s" % tool_path)
        if not (root / tool_path).exists():
            issues.append("CLI fixture tool missing on disk: %s" % tool_path)

    readme_tools = sorted(set(re.findall(r"tools/[A-Za-z0-9_./-]+\.py", readme_content)))
    missing_readme_tools = [tool_path for tool_path in readme_tools if not (root / tool_path).exists()]
    for tool_path in missing_readme_tools:
        issues.append("README lists missing tool on disk: %s" % tool_path)

    state = STATE_OK if not issues else STATE_ERROR
    return ComponentStatus(
        name="cli_readme_tools",
        state=state,
        issues=issues,
        details={
            "fixture_path": str(fixture_path),
            "cli_fixture_tool_count": len(cli_tool_paths),
            "readme_tool_count": len(readme_tools),
        },
    )


def _check_artifacts_alignment(readme_content: str, workflow_content: str) -> ComponentStatus:
    issues: list[str] = []

    documented_artifacts = sorted(set(re.findall(r"support-metrics-[a-z0-9-]+", readme_content)))
    workflow_artifacts = sorted(
        set(
            re.findall(
                r"(?m)^\s*name:\s*(support-metrics-[a-z0-9-]+)\s*$",
                workflow_content,
            )
        )
    )

    for artifact_name in REQUIRED_ARTIFACT_NAMES:
        if artifact_name not in readme_content:
            issues.append("README missing required artifact mention: %s" % artifact_name)
        if artifact_name not in workflow_content:
            issues.append("workflow missing required artifact mention: %s" % artifact_name)

    for artifact_name in documented_artifacts:
        if artifact_name not in workflow_content:
            issues.append("README documents artifact not found in workflow: %s" % artifact_name)

    for artifact_name in workflow_artifacts:
        if artifact_name not in readme_content:
            issues.append("workflow artifact not documented in README: %s" % artifact_name)

    state = STATE_OK if not issues else STATE_ERROR
    return ComponentStatus(
        name="artifacts_alignment",
        state=state,
        issues=issues,
        details={
            "required_artifacts": list(REQUIRED_ARTIFACT_NAMES),
            "documented_artifacts": documented_artifacts,
            "workflow_artifacts": workflow_artifacts,
        },
    )


def _check_fragments_coverage(root: Path) -> ComponentStatus:
    issues: list[str] = []
    fragments_dir = root / "tests" / "fixtures" / "support_metrics_ci_outputs"
    result = inspect_fragment_directory(fragments_dir)
    issues.extend(result.issues)

    known_categories = set(EXPECTED_CATEGORIES)
    missing_known_categories = [
        category
        for category in REQUIRED_FRAGMENT_CATEGORIES
        if category not in known_categories
    ]
    for category in missing_known_categories:
        issues.append("fragments tool missing known category: %s" % category)

    covered_categories = sorted(
        {
            file_status.category
            for file_status in result.files
            if file_status.status == "ok"
        }
    )
    for category in REQUIRED_FRAGMENT_CATEGORIES:
        if category not in covered_categories:
            issues.append("fragments fixtures missing coverage for category: %s" % category)

    state = STATE_OK if not issues else STATE_ERROR
    return ComponentStatus(
        name="fragments_coverage",
        state=state,
        issues=issues,
        details={
            "fragments_dir": str(fragments_dir),
            "covered_categories": covered_categories,
            "expected_categories": list(REQUIRED_FRAGMENT_CATEGORIES),
        },
    )


def _check_workflow_rules(workflow_content: str) -> ComponentStatus:
    issues: list[str] = []

    for snippet in REQUIRED_WORKFLOW_STEP_SNIPPETS:
        if snippet not in workflow_content:
            issues.append("workflow missing required step snippet: %s" % snippet)

    if "--fail-on-regression" in workflow_content:
        issues.append("workflow contains forbidden option: --fail-on-regression")

    smoke_block = _extract_step_block(workflow_content, "Smoke test support metrics CI summary")
    runtime_block = _extract_step_block(workflow_content, "Optional runtime support metrics CI check")

    if smoke_block == "":
        issues.append("workflow missing smoke step block")
    else:
        if "recent_complete.jsonl" not in smoke_block:
            issues.append("smoke step missing recent_complete.jsonl fixture")
        if "outputs/ci" in smoke_block:
            issues.append("outputs/ci must not be used in smoke step")
        if "$env:SUPPORT_METRICS_BASELINE_PATH" in smoke_block:
            issues.append("smoke step must not use runtime baseline env path")
        if "$env:SUPPORT_METRICS_CURRENT_PATH" in smoke_block:
            issues.append("smoke step must not use runtime current env path")

    if runtime_block == "":
        issues.append("workflow missing runtime step block")
    else:
        if "$env:SUPPORT_METRICS_BASELINE_PATH" not in runtime_block:
            issues.append("runtime step missing baseline env path")
        if "$env:SUPPORT_METRICS_CURRENT_PATH" not in runtime_block:
            issues.append("runtime step missing current env path")
        if "recent_complete.jsonl" in runtime_block:
            issues.append("recent_complete.jsonl must not be used in runtime step")

    outputs_ci_lines = [line.strip() for line in workflow_content.splitlines() if "outputs/ci" in line]
    if len(outputs_ci_lines) == 0:
        issues.append("workflow missing outputs/ci references for optional runtime configuration")
    for line in outputs_ci_lines:
        lower_line = line.lower()
        allowed = (
            line.startswith("SUPPORT_METRICS_BASELINE_PATH: outputs/ci/"),
            line.startswith("SUPPORT_METRICS_CURRENT_PATH: outputs/ci/"),
            "runtime" in lower_line,
        )
        if not any(allowed):
            issues.append("outputs/ci used outside runtime-only context: %s" % line)

    state = STATE_OK if not issues else STATE_ERROR
    return ComponentStatus(
        name="workflow_rules",
        state=state,
        issues=issues,
        details={
            "required_step_snippets": list(REQUIRED_WORKFLOW_STEP_SNIPPETS),
            "outputs_ci_reference_count": len(outputs_ci_lines),
        },
    )


def _check_tool_scripts(root: Path) -> ComponentStatus:
    issues: list[str] = []
    health_path = root / "tools" / "check_support_metrics_ci_health.py"
    fragments_path = root / "tools" / "check_support_metrics_ci_fragments.py"

    if not health_path.exists():
        issues.append("missing tool script: tools/check_support_metrics_ci_health.py")
    if not fragments_path.exists():
        issues.append("missing tool script: tools/check_support_metrics_ci_fragments.py")

    if health_path.exists():
        content, error = _load_text(health_path)
        if error != "":
            issues.append("cannot read health tool script: %s" % error)
        else:
            if "inspect_fragment_directory" not in content:
                issues.append("health tool missing inspect_fragment_directory usage")
            if "CLI_HELP_CONTRACT_RELATIVE_PATH" not in content:
                issues.append("health tool missing CLI_HELP_CONTRACT_RELATIVE_PATH")

    if fragments_path.exists():
        content, error = _load_text(fragments_path)
        if error != "":
            issues.append("cannot read fragments tool script: %s" % error)
        else:
            for category in REQUIRED_FRAGMENT_CATEGORIES:
                if re.search(r"""['"]%s['"]""" % re.escape(category), content) is None:
                    issues.append("fragments tool missing category token: %s" % category)

    state = STATE_OK if not issues else STATE_ERROR
    return ComponentStatus(
        name="tool_scripts",
        state=state,
        issues=issues,
        details={
            "health_script": str(health_path),
            "fragments_script": str(fragments_path),
        },
    )


def build_contract_audit(root: Path) -> ContractAuditReport:
    readme_path = root / "README.md"
    workflow_path = root / ".github" / "workflows" / "tests.yml"

    readme_content, readme_error = _load_text(readme_path)
    workflow_content, workflow_error = _load_text(workflow_path)

    pre_issues: list[str] = []
    if readme_error != "":
        pre_issues.append("cannot read README.md: %s" % readme_error)
    if workflow_error != "":
        pre_issues.append("cannot read workflow tests.yml: %s" % workflow_error)

    cli_readme_tools = _check_cli_readme_tools(root, readme_content)
    if readme_error != "":
        cli_readme_tools.state = STATE_ERROR
        cli_readme_tools.issues = pre_issues + cli_readme_tools.issues

    artifacts_alignment = _check_artifacts_alignment(readme_content, workflow_content)
    if readme_error != "" or workflow_error != "":
        artifacts_alignment.state = STATE_ERROR
        artifacts_alignment.issues = pre_issues + artifacts_alignment.issues

    fragments_coverage = _check_fragments_coverage(root)
    workflow_rules = _check_workflow_rules(workflow_content)
    if workflow_error != "":
        workflow_rules.state = STATE_ERROR
        workflow_rules.issues = pre_issues + workflow_rules.issues

    tool_scripts = _check_tool_scripts(root)

    overall = _worst_state(
        [
            cli_readme_tools.state,
            artifacts_alignment.state,
            fragments_coverage.state,
            workflow_rules.state,
            tool_scripts.state,
        ]
    )

    return ContractAuditReport(
        cli_readme_tools=cli_readme_tools,
        artifacts_alignment=artifacts_alignment,
        fragments_coverage=fragments_coverage,
        workflow_rules=workflow_rules,
        tool_scripts=tool_scripts,
        overall=overall,
    )


def _print_text_report(report: ContractAuditReport, verbose: bool) -> None:
    print("Support metrics CI contract audit:")
    print("- cli_readme_tools: %s" % report.cli_readme_tools.state)
    print("- artifacts_alignment: %s" % report.artifacts_alignment.state)
    print("- fragments_coverage: %s" % report.fragments_coverage.state)
    print("- workflow_rules: %s" % report.workflow_rules.state)
    print("- tool_scripts: %s" % report.tool_scripts.state)
    print("- overall: %s" % report.overall)

    if not verbose:
        return

    for component in (
        report.cli_readme_tools,
        report.artifacts_alignment,
        report.fragments_coverage,
        report.workflow_rules,
        report.tool_scripts,
    ):
        print("")
        print("%s details:" % component.name)
        if not component.issues:
            print("- no issues")
            continue
        for issue in component.issues:
            print("- %s" % issue)


def _state_from_components(states: list[str]) -> str:
    return _worst_state(states)


def _build_markdown_report(report: ContractAuditReport) -> str:
    readme_state = _state_from_components([report.cli_readme_tools.state])
    workflow_state = _state_from_components([report.workflow_rules.state])
    tools_state = _state_from_components([report.tool_scripts.state, report.cli_readme_tools.state])
    fixtures_state = _state_from_components([report.fragments_coverage.state, report.cli_readme_tools.state])
    fragments_state = _state_from_components([report.fragments_coverage.state])
    artifacts_state = _state_from_components([report.artifacts_alignment.state])

    lines: list[str] = []
    lines.append("# Support metrics CI contract audit")
    lines.append("")
    lines.append("- overall: %s" % report.overall)
    lines.append("- README: %s" % readme_state)
    lines.append("- workflow: %s" % workflow_state)
    lines.append("- tools: %s" % tools_state)
    lines.append("- fixtures: %s" % fixtures_state)
    lines.append("- fragments: %s" % fragments_state)
    lines.append("- artifacts: %s" % artifacts_state)
    lines.append("- interpretation: maintenance CI/debug only, not gameplay validation")
    return "\n".join(lines) + "\n"


def _write_markdown_report(path: Path, report: ContractAuditReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_build_markdown_report(report), encoding="utf-8")


def main() -> int:
    args = _build_parser().parse_args()
    report = build_contract_audit(args.root)

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
