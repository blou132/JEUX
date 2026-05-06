from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.support_metrics_output_fragments import assert_expected_fragments_present


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "audit_support_metrics_ci_contract.py"
OUTPUT_CONTRACT_FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_ci_outputs"

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
EXPECTED_CLI_FIXTURE_TOOLS: tuple[str, ...] = (
    "tools/analyze_run_metrics_history.py",
    "tools/write_support_metrics_ci_summary.py",
    "tools/simulate_support_metrics_ci.py",
    "tools/check_support_metrics_ci_fragments.py",
    "tools/check_support_metrics_ci_health.py",
)
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
env:
  SUPPORT_METRICS_BASELINE_PATH: outputs/ci/support_metrics_baseline.jsonl
  SUPPORT_METRICS_CURRENT_PATH: outputs/ci/support_metrics_current.jsonl
  SUPPORT_METRICS_REPORT_PATH: artifacts/support_metrics_report.md
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
      - name: Upload support metrics CI contract audit artifact
        uses: actions/upload-artifact@v4
        with:
          name: support-metrics-ci-contract-audit
          path: artifacts/support_metrics_ci_contract_audit.md
          if-no-files-found: error
      - name: Validate support metrics CI health
        run: py tools/check_support_metrics_ci_health.py --check --markdown-output artifacts/support_metrics_ci_health.md
      - name: Upload support metrics CI health artifact
        uses: actions/upload-artifact@v4
        with:
          name: support-metrics-ci-health
          path: artifacts/support_metrics_ci_health.md
          if-no-files-found: error
      - name: Smoke test support metrics CI summary (technical fixtures)
        run: |
          py tools/write_support_metrics_ci_summary.py `
            --ci-check `
            --baseline tests/fixtures/support_metrics_contract/recent_complete.jsonl `
            --current tests/fixtures/support_metrics_contract/recent_complete.jsonl `
            --report-output artifacts/support_metrics_smoke_report.md `
            --artifact-name "support-metrics-smoke-report"
      - name: Upload support metrics smoke report artifact (technical fixtures)
        uses: actions/upload-artifact@v4
        with:
          name: support-metrics-smoke-report
          path: artifacts/support_metrics_smoke_report.md
          if-no-files-found: error
      - name: Optional runtime support metrics CI check (outputs/ci)
        run: |
          py tools/write_support_metrics_ci_summary.py `
            --ci-check `
            --baseline "$env:SUPPORT_METRICS_BASELINE_PATH" `
            --current "$env:SUPPORT_METRICS_CURRENT_PATH" `
            --report-output "$env:SUPPORT_METRICS_REPORT_PATH" `
            --artifact-name "support-metrics-report"
      - name: Upload support metrics runtime report artifact (optional)
        uses: actions/upload-artifact@v4
        with:
          name: support-metrics-report
          path: artifacts/support_metrics_report.md
          if-no-files-found: ignore
"""


VALID_README_CONTENT = """# README
Support metrics tools index
tools/analyze_run_metrics_history.py
tools/write_support_metrics_ci_summary.py
tools/simulate_support_metrics_ci.py
tools/check_support_metrics_ci_fragments.py
tools/check_support_metrics_ci_health.py
support-metrics-smoke-report
support-metrics-report
support-metrics-ci-health
support-metrics-ci-contract-audit
CI/debug only
not gameplay validation
runtime report optional
no --fail-on-regression by default
"""


def _run_audit_tool(extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    command: list[str] = [sys.executable, str(SCRIPT)]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _write_minimal_valid_root(root_dir: Path) -> None:
    tools_dir = root_dir / "tools"
    fixtures_dir = root_dir / "tests" / "fixtures"
    contract_dir = fixtures_dir / "support_metrics_contract"
    fragments_dir = fixtures_dir / "support_metrics_ci_outputs"
    workflow_dir = root_dir / ".github" / "workflows"

    tools_dir.mkdir(parents=True, exist_ok=True)
    contract_dir.mkdir(parents=True, exist_ok=True)
    fragments_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    for tool_path in EXPECTED_CLI_FIXTURE_TOOLS:
        (root_dir / tool_path).parent.mkdir(parents=True, exist_ok=True)
        (root_dir / tool_path).write_text("# stub\n", encoding="utf-8")

    # Extra expected tooling files referenced by the audit scope.
    (tools_dir / "check_support_metrics_ci_health.py").write_text(
        "from check_support_metrics_ci_fragments import inspect_fragment_directory\n"
        "CLI_HELP_CONTRACT_RELATIVE_PATH = 'tests/fixtures/support_metrics_cli_help_expected.json'\n",
        encoding="utf-8",
    )
    (tools_dir / "check_support_metrics_ci_fragments.py").write_text(
        "EXPECTED_FRAGMENT_FILES = ()\n"
        "EXPECTED_CATEGORIES = ('manifest', 'health', 'contract_audit', 'smoke', 'runtime', 'error', 'local')\n",
        encoding="utf-8",
    )

    (fixtures_dir / "support_metrics_cli_help_expected.json").write_text(
        json.dumps(
            {
                "tools": [
                    {"path": tool_path, "options": ["--help"]}
                    for tool_path in EXPECTED_CLI_FIXTURE_TOOLS
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (fixtures_dir / "support_metrics_ci_contract_manifest.json").write_text(
        json.dumps(TEMP_ROOT_CONTRACT_MANIFEST, indent=2),
        encoding="utf-8",
    )
    (contract_dir / "recent_complete.jsonl").write_text("{\"ok\": true}\n", encoding="utf-8")

    for file_name in EXPECTED_FRAGMENT_FILES:
        (fragments_dir / file_name).write_text("required fragment\n", encoding="utf-8")

    (root_dir / "README.md").write_text(VALID_README_CONTENT, encoding="utf-8")
    (workflow_dir / "tests.yml").write_text(VALID_WORKFLOW_CONTENT, encoding="utf-8")


class AuditSupportMetricsCIContractToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_audit_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--json", result.stdout)
        self.assertIn("--check", result.stdout)
        self.assertIn("--verbose", result.stdout)
        self.assertIn("--root", result.stdout)
        self.assertIn("--markdown-output", result.stdout)

    def test_audit_nominal_is_ok(self) -> None:
        result = _run_audit_tool(["--check"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics CI contract audit:", result.stdout)
        self.assertIn("- overall: ok", result.stdout)

    def test_readme_missing_expected_artifact_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            readme_path = temp_root / "README.md"
            readme_path.write_text(
                readme_path.read_text(encoding="utf-8").replace(
                    "support-metrics-report",
                    "support-metrics-runtime-report",
                    1,
                ),
                encoding="utf-8",
            )

            result = _run_audit_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- artifacts_alignment: error", result.stdout)
            self.assertIn("README missing required artifact mention: support-metrics-report", result.stdout)

    def test_workflow_missing_expected_artifact_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            workflow_path = temp_root / ".github" / "workflows" / "tests.yml"
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8").replace(
                    "name: support-metrics-report",
                    "name: support-metrics-runtime-report",
                    1,
                ),
                encoding="utf-8",
            )

            result = _run_audit_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- artifacts_alignment: error", result.stdout)
            self.assertIn("support-metrics-runtime-report", result.stdout)

    def test_cli_fixture_with_missing_tool_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            fixture_path = temp_root / "tests" / "fixtures" / "support_metrics_cli_help_expected.json"
            parsed = json.loads(fixture_path.read_text(encoding="utf-8"))
            parsed["tools"].append({"path": "tools/missing_contract_tool.py", "options": ["--help"]})
            fixture_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

            result = _run_audit_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- cli_readme_tools: error", result.stdout)
            self.assertIn("CLI fixture tool missing on disk: tools/missing_contract_tool.py", result.stdout)

    def test_workflow_with_fail_on_regression_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_minimal_valid_root(temp_root)
            workflow_path = temp_root / ".github" / "workflows" / "tests.yml"
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8")
                + "\n      - name: forbidden\n        run: py tools/analyze_run_metrics_history.py --fail-on-regression\n",
                encoding="utf-8",
            )

            result = _run_audit_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- workflow_rules: error", result.stdout)
            self.assertIn("workflow contains forbidden option: --fail-on-regression", result.stdout)

    def test_json_output_is_valid(self) -> None:
        result = _run_audit_tool(["--json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        parsed = json.loads(result.stdout)
        self.assertIsInstance(parsed, dict)
        self.assertIn("overall", parsed)
        self.assertIn("cli_readme_tools", parsed)
        self.assertIn("artifacts_alignment", parsed)
        self.assertIn("fragments_coverage", parsed)
        self.assertIn("workflow_rules", parsed)
        self.assertIn("tool_scripts", parsed)

    def test_text_output_contains_overall(self) -> None:
        result = _run_audit_tool([])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics CI contract audit:", result.stdout)
        self.assertIn("- overall:", result.stdout)

    def test_markdown_report_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_contract_audit.md"
            result = _run_audit_tool(["--check", "--markdown-output", str(output_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Support metrics CI contract audit", content)
            self.assertIn("- overall:", content)
            self.assertIn("- README:", content)
            self.assertIn("- workflow:", content)
            self.assertIn("- tools:", content)
            self.assertIn("- fixtures:", content)
            self.assertIn("- fragments:", content)
            self.assertIn("- artifacts:", content)
            self.assertIn("not gameplay validation", content)

    def test_contract_audit_report_matches_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_contract_audit.md"
            result = _run_audit_tool(["--check", "--markdown-output", str(report_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                report_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "contract_audit_report_expected_fragments.txt",
            )

    def test_contract_audit_summary_matches_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_contract_audit.md"
            summary_path = Path(tmpdir) / "artifacts" / "github_step_summary.md"
            result = _run_audit_tool(["--check", "--markdown-output", str(report_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())

            report_text = report_path.read_text(encoding="utf-8")
            summary_path.write_text("## CI Summary\n\n" + report_text, encoding="utf-8")
            summary_text = summary_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                summary_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "contract_audit_summary_expected_fragments.txt",
            )


if __name__ == "__main__":
    unittest.main()
