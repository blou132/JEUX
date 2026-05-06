from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.support_metrics_output_fragments import assert_expected_fragments_present


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_support_metrics_ci_health.py"
OUTPUT_CONTRACT_FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_ci_outputs"
EXPECTED_TOOL_FILES: tuple[str, ...] = (
    "analyze_run_metrics_history.py",
    "write_support_metrics_ci_summary.py",
    "simulate_support_metrics_ci.py",
    "check_support_metrics_ci_fragments.py",
    "audit_support_metrics_ci_contract.py",
)
EXPECTED_README_SNIPPETS: tuple[str, ...] = (
    "Support metrics tools index",
    "tools/analyze_run_metrics_history.py",
    "tools/write_support_metrics_ci_summary.py",
    "tools/simulate_support_metrics_ci.py",
    "tools/check_support_metrics_ci_fragments.py",
    "tools/check_support_metrics_ci_health.py",
    "tools/audit_support_metrics_ci_contract.py",
    "Support metrics CI contract audit artifact",
    "CI/debug only",
    "not gameplay validation",
    "runtime report optional",
    "no --fail-on-regression by default",
)
EXPECTED_FRAGMENT_FILES: tuple[str, ...] = (
    "manifest_summary_expected_fragments.txt",
    "manifest_report_expected_fragments.txt",
    "health_summary_expected_fragments.txt",
    "health_report_expected_fragments.txt",
    "contract_audit_summary_expected_fragments.txt",
    "contract_audit_report_expected_fragments.txt",
    "smoke_summary_expected_fragments.txt",
    "smoke_report_expected_fragments.txt",
    "runtime_skip_summary_expected_fragments.txt",
    "runtime_skip_report_expected_fragments.txt",
    "error_summary_expected_fragments.txt",
    "error_report_expected_fragments.txt",
    "local_simulation_summary_expected_fragments.txt",
    "local_simulation_report_expected_fragments.txt",
)
TEMP_ROOT_CLI_HELP_TOOLS: list[dict[str, object]] = [
    {
        "path": "tools/analyze_run_metrics_history.py",
        "options": [
            "--input",
            "--compare-input",
            "--ci-check",
            "--format",
            "--fail-on-regression",
        ],
    },
    {
        "path": "tools/write_support_metrics_ci_summary.py",
        "options": [
            "--baseline",
            "--current",
            "--report-output",
            "--step-summary",
            "--artifact-name",
            "--ci-check",
            "--strict",
            "--analyze-script",
            "--report-mode",
            "--input-label",
            "--compare-input-label",
        ],
    },
    {
        "path": "tools/simulate_support_metrics_ci.py",
        "options": [
            "--baseline",
            "--current",
            "--output-dir",
            "--strict",
            "--analyze-script",
            "--report-mode",
        ],
    },
    {
        "path": "tools/check_support_metrics_ci_fragments.py",
        "options": ["--list", "--validate", "--print-missing"],
    },
    {
        "path": "tools/check_support_metrics_ci_health.py",
        "options": ["--check", "--json", "--verbose", "--markdown-output"],
    },
    {
        "path": "tools/audit_support_metrics_ci_contract.py",
        "options": ["--json", "--check", "--verbose", "--markdown-output"],
    },
]
TEMP_ROOT_CONTRACT_MANIFEST: dict[str, list[str]] = {
    "tools": [
        "tools/analyze_run_metrics_history.py",
        "tools/write_support_metrics_ci_summary.py",
        "tools/simulate_support_metrics_ci.py",
        "tools/check_support_metrics_ci_fragments.py",
        "tools/check_support_metrics_ci_health.py",
        "tools/audit_support_metrics_ci_contract.py",
    ],
    "artifacts": [
        "support-metrics-smoke-report",
        "support-metrics-report",
        "support-metrics-ci-health",
        "support-metrics-ci-contract-audit",
    ],
    "fragment_categories": [
        "manifest",
        "smoke",
        "runtime",
        "error",
        "local",
        "health",
        "contract_audit",
    ],
    "workflow_steps": [
        "Run unit tests",
        "Validate support metrics CI fragments",
        "Validate support metrics CI contract audit",
        "Validate support metrics CI health",
        "Smoke test support metrics CI summary",
        "Optional runtime support metrics CI check",
    ],
    "expected_invariants": [
        "CI/debug only",
        "not gameplay validation",
        "runtime report optional",
        "no --fail-on-regression by default",
    ],
    "report_modes": ["smoke", "runtime", "local", "health", "contract_audit"],
}


VALID_WORKFLOW_CONTENT = """name: Tests
jobs:
  tests:
    runs-on: windows-latest
    steps:
      - name: Run unit tests
        run: py -m unittest discover -s tests -p "test_*.py"
      - name: Validate support metrics CI fragments
        run: py tools/check_support_metrics_ci_fragments.py --validate
      - name: Validate support metrics CI contract audit
        run: py tools/audit_support_metrics_ci_contract.py --check --markdown-output artifacts/support_metrics_ci_contract_audit.md
      - uses: actions/upload-artifact@v4
        with:
          name: support-metrics-ci-contract-audit
          path: artifacts/support_metrics_ci_contract_audit.md
          if-no-files-found: error
      - name: Validate support metrics CI health
        run: |
          py tools/check_support_metrics_ci_health.py --check --markdown-output artifacts/support_metrics_ci_health.md
          Get-Content artifacts/support_metrics_ci_health.md | Add-Content -Path $env:GITHUB_STEP_SUMMARY
      - uses: actions/upload-artifact@v4
        with:
          name: support-metrics-ci-health
          path: artifacts/support_metrics_ci_health.md
          if-no-files-found: error
      - name: Smoke test support metrics CI summary (technical fixtures)
        run: py tools/write_support_metrics_ci_summary.py --artifact-name "support-metrics-smoke-report"
      - name: Optional runtime support metrics CI check (outputs/ci)
        run: py tools/write_support_metrics_ci_summary.py --artifact-name "support-metrics-report"
      - uses: actions/upload-artifact@v4
        with:
          name: support-metrics-smoke-report
          if-no-files-found: error
      - uses: actions/upload-artifact@v4
        with:
          name: support-metrics-report
          if-no-files-found: ignore
"""


def _run_health_tool(extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    command: list[str] = [sys.executable, str(SCRIPT)]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _write_dummy_cli_tool(path: Path, options: list[str]) -> None:
    unique_options: list[str] = []
    for option in options:
        normalized = str(option).strip()
        if normalized == "":
            continue
        if normalized not in unique_options:
            unique_options.append(normalized)

    option_lines = "\n".join(
        [
            "    parser.add_argument(%r, action='store_true')" % option
            for option in unique_options
        ]
    )
    content = (
        "from __future__ import annotations\n"
        "import argparse\n\n"
        "def main() -> int:\n"
        "    parser = argparse.ArgumentParser(description='dummy support metrics tool')\n"
        f"{option_lines}\n"
        "    parser.parse_args()\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_minimal_valid_root(root_dir: Path) -> None:
    tools_dir = root_dir / "tools"
    contract_dir = root_dir / "tests" / "fixtures" / "support_metrics_contract"
    fragments_dir = root_dir / "tests" / "fixtures" / "support_metrics_ci_outputs"
    workflow_dir = root_dir / ".github" / "workflows"

    tools_dir.mkdir(parents=True, exist_ok=True)
    contract_dir.mkdir(parents=True, exist_ok=True)
    fragments_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    for file_name in EXPECTED_TOOL_FILES:
        (tools_dir / file_name).write_text("# stub\n", encoding="utf-8")
    for tool_entry in TEMP_ROOT_CLI_HELP_TOOLS:
        _write_dummy_cli_tool(
            root_dir / str(tool_entry["path"]),
            [str(option) for option in list(tool_entry["options"])],
        )

    (contract_dir / "recent_complete.jsonl").write_text("{\"ok\": true}\n", encoding="utf-8")

    for file_name in EXPECTED_FRAGMENT_FILES:
        (fragments_dir / file_name).write_text("required fragment\n", encoding="utf-8")

    (workflow_dir / "tests.yml").write_text(VALID_WORKFLOW_CONTENT, encoding="utf-8")
    (root_dir / "tests" / "fixtures").mkdir(parents=True, exist_ok=True)
    (root_dir / "tests" / "fixtures" / "support_metrics_cli_help_expected.json").write_text(
        json.dumps({"tools": TEMP_ROOT_CLI_HELP_TOOLS}, indent=2),
        encoding="utf-8",
    )
    (root_dir / "tests" / "fixtures" / "support_metrics_ci_contract_manifest.json").write_text(
        json.dumps(TEMP_ROOT_CONTRACT_MANIFEST, indent=2),
        encoding="utf-8",
    )
    (root_dir / "README.md").write_text(
        "\n".join(EXPECTED_README_SNIPPETS) + "\n",
        encoding="utf-8",
    )


class CheckSupportMetricsCIHealthToolTests(unittest.TestCase):
    def test_help_exposes_check_json_verbose_options(self) -> None:
        result = _run_health_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--check", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--verbose", result.stdout)
        self.assertIn("--markdown-output", result.stdout)

    def test_health_nominal_is_ok(self) -> None:
        result = _run_health_tool(["--check"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics CI health:", result.stdout)
        self.assertIn("- documentation: ok", result.stdout)
        self.assertIn("- cli_help: ok", result.stdout)
        self.assertIn("- contract_audit: ok", result.stdout)
        self.assertIn("- overall: ok", result.stdout)

    def test_missing_tool_file_in_temp_root_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "tools" / "simulate_support_metrics_ci.py").unlink()

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- tools: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("missing tool: tools/simulate_support_metrics_ci.py", result.stdout)

    def test_workflow_without_smoke_report_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            workflow_path = temp_root / ".github" / "workflows" / "tests.yml"
            content = workflow_path.read_text(encoding="utf-8")
            content = content.replace(
                '      - name: Smoke test support metrics CI summary (technical fixtures)\n'
                '        run: py tools/write_support_metrics_ci_summary.py --artifact-name "support-metrics-smoke-report"\n',
                "",
            )
            workflow_path.write_text(content, encoding="utf-8")

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- workflow: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("workflow missing snippet: Smoke test support metrics CI summary (technical fixtures)", result.stdout)

    def test_workflow_with_fail_on_regression_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            workflow_path = temp_root / ".github" / "workflows" / "tests.yml"
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8")
                + "\n      - name: Bad regression\n        run: py tools/analyze_run_metrics_history.py --fail-on-regression\n",
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- workflow: warning", result.stdout)
            self.assertIn("- overall: warning", result.stdout)
            self.assertIn("workflow contains forbidden snippet: --fail-on-regression", result.stdout)

    def test_workflow_without_contract_audit_step_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            workflow_path = temp_root / ".github" / "workflows" / "tests.yml"
            content = workflow_path.read_text(encoding="utf-8")
            content = content.replace(
                '      - name: Validate support metrics CI contract audit\n'
                '        run: py tools/audit_support_metrics_ci_contract.py --check --markdown-output artifacts/support_metrics_ci_contract_audit.md\n',
                "",
            )
            workflow_path.write_text(content, encoding="utf-8")

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- contract_audit: error", result.stdout)
            self.assertIn(
                "workflow missing contract audit snippet: Validate support metrics CI contract audit",
                result.stdout,
            )

    def test_workflow_without_contract_audit_artifact_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            workflow_path = temp_root / ".github" / "workflows" / "tests.yml"
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8").replace(
                    "name: support-metrics-ci-contract-audit",
                    "name: contract-audit-artifact-missing",
                ),
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- contract_audit: error", result.stdout)
            self.assertIn(
                "workflow missing contract audit snippet: support-metrics-ci-contract-audit",
                result.stdout,
            )

    def test_contract_audit_tool_missing_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "tools" / "audit_support_metrics_ci_contract.py").unlink()

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- contract_audit: error", result.stdout)
            self.assertIn("missing contract audit tool:", result.stdout)
            self.assertIn("audit_support_metrics_ci_contract.py", result.stdout)

    def test_contract_manifest_missing_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "tests" / "fixtures" / "support_metrics_ci_contract_manifest.json").unlink()

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- contract_audit: error", result.stdout)
            self.assertIn("contract manifest issue:", result.stdout)
            self.assertIn("support_metrics_ci_contract_manifest.json", result.stdout)

    def test_contract_manifest_invalid_json_is_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            manifest_path = temp_root / "tests" / "fixtures" / "support_metrics_ci_contract_manifest.json"
            manifest_path.write_text("{invalid json", encoding="utf-8")

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- contract_audit: error", result.stdout)
            self.assertIn("contract manifest issue:", result.stdout)
            self.assertIn("invalid JSON", result.stdout)

    def test_json_output_is_valid(self) -> None:
        result = _run_health_tool(["--json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        parsed = json.loads(result.stdout)
        self.assertIsInstance(parsed, dict)
        self.assertIn("overall", parsed)
        self.assertIn("tools", parsed)
        self.assertIn("workflow", parsed)
        self.assertIn("fragments", parsed)
        self.assertIn("documentation", parsed)
        self.assertIn("cli_help", parsed)
        self.assertIn("contract_audit", parsed)

    def test_text_output_contains_overall(self) -> None:
        result = _run_health_tool([])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics CI health:", result.stdout)
        self.assertIn("- documentation:", result.stdout)
        self.assertIn("- cli_help:", result.stdout)
        self.assertIn("- contract_audit:", result.stdout)
        self.assertIn("- overall:", result.stdout)

    def test_fragments_are_checked_via_v191_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            # Force an invalid fragments contract by emptying one required file.
            (temp_root / "tests" / "fixtures" / "support_metrics_ci_outputs" / "smoke_report_expected_fragments.txt").write_text(
                "# comment only\n",
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- fragments: error", result.stdout)
            self.assertIn("empty fragment file (no non-comment fragments): smoke_report_expected_fragments.txt", result.stdout)

    def test_contract_audit_fragments_are_checked_via_v191_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "tests" / "fixtures" / "support_metrics_ci_outputs" / "contract_audit_report_expected_fragments.txt").write_text(
                "# comment only\n",
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- fragments: error", result.stdout)
            self.assertIn(
                "empty fragment file (no non-comment fragments): contract_audit_report_expected_fragments.txt",
                result.stdout,
            )

    def test_markdown_report_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_health.md"
            result = _run_health_tool(["--check", "--markdown-output", str(output_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Support metrics CI health", content)
            self.assertIn("- documentation:", content)
            self.assertIn("- cli_help:", content)
            self.assertIn("- contract_audit:", content)
            self.assertIn("- overall:", content)
            self.assertIn("not gameplay validation", content)

    def test_missing_readme_in_temp_root_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "README.md").unlink()

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- documentation: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("missing documentation file: README.md", result.stdout)

    def test_readme_without_tools_index_section_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            readme_path = temp_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "Support metrics tools index",
                    "Support metrics tools",
                ),
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- documentation: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("README missing snippet: Support metrics tools index", result.stdout)

    def test_readme_without_expected_tool_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            readme_path = temp_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "tools/simulate_support_metrics_ci.py",
                    "tools/simulate_support_metrics_ci",
                ),
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- documentation: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn(
                "README missing snippet: tools/simulate_support_metrics_ci.py",
                result.stdout,
            )

    def test_missing_cli_help_fixture_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "tests" / "fixtures" / "support_metrics_cli_help_expected.json").unlink()

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- cli_help: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("missing CLI help contract fixture", result.stdout)

    def test_cli_help_tool_listed_but_missing_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            (temp_root / "tools" / "simulate_support_metrics_ci.py").unlink()

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- cli_help: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("CLI help tool missing: tools/simulate_support_metrics_ci.py", result.stdout)

    def test_cli_help_non_zero_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            failing_tool = temp_root / "tools" / "check_support_metrics_ci_fragments.py"
            failing_tool.write_text(
                "from __future__ import annotations\n"
                "import sys\n"
                "raise SystemExit(2)\n",
                encoding="utf-8",
            )

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- cli_help: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn(
                "CLI help returned non-zero for tools/check_support_metrics_ci_fragments.py",
                result.stdout,
            )

    def test_cli_help_missing_expected_option_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            fixture_path = temp_root / "tests" / "fixtures" / "support_metrics_cli_help_expected.json"
            parsed = json.loads(fixture_path.read_text(encoding="utf-8"))
            for tool_entry in parsed["tools"]:
                if tool_entry["path"] == "tools/write_support_metrics_ci_summary.py":
                    tool_entry["options"].append("--missing-contract-option")
                    break
            fixture_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

            result = _run_health_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- cli_help: error", result.stdout)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn(
                "CLI help missing option --missing-contract-option for tools/write_support_metrics_ci_summary.py",
                result.stdout,
            )

    def test_health_report_matches_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_health.md"
            result = _run_health_tool(["--check", "--markdown-output", str(report_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                report_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "health_report_expected_fragments.txt",
            )

    def test_health_summary_matches_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_health.md"
            summary_path = Path(tmpdir) / "artifacts" / "github_step_summary.md"
            result = _run_health_tool(["--check", "--markdown-output", str(report_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())

            report_text = report_path.read_text(encoding="utf-8")
            summary_path.write_text(
                "## CI Summary\n\n" + report_text,
                encoding="utf-8",
            )
            summary_text = summary_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                summary_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "health_summary_expected_fragments.txt",
            )


if __name__ == "__main__":
    unittest.main()
