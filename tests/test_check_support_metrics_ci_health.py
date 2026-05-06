from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_support_metrics_ci_health.py"
EXPECTED_TOOL_FILES: tuple[str, ...] = (
    "analyze_run_metrics_history.py",
    "write_support_metrics_ci_summary.py",
    "simulate_support_metrics_ci.py",
    "check_support_metrics_ci_fragments.py",
)
EXPECTED_FRAGMENT_FILES: tuple[str, ...] = (
    "smoke_summary_expected_fragments.txt",
    "smoke_report_expected_fragments.txt",
    "runtime_skip_summary_expected_fragments.txt",
    "runtime_skip_report_expected_fragments.txt",
    "error_summary_expected_fragments.txt",
    "error_report_expected_fragments.txt",
    "local_simulation_summary_expected_fragments.txt",
    "local_simulation_report_expected_fragments.txt",
)


VALID_WORKFLOW_CONTENT = """name: Tests
jobs:
  tests:
    runs-on: windows-latest
    steps:
      - name: Run unit tests
        run: py -m unittest discover -s tests -p "test_*.py"
      - name: Validate support metrics CI fragments
        run: py tools/check_support_metrics_ci_fragments.py --validate
      - name: Validate support metrics CI health
        run: py tools/check_support_metrics_ci_health.py --check --markdown-output artifacts/support_metrics_ci_health.md
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

    (contract_dir / "recent_complete.jsonl").write_text("{\"ok\": true}\n", encoding="utf-8")

    for file_name in EXPECTED_FRAGMENT_FILES:
        (fragments_dir / file_name).write_text("required fragment\n", encoding="utf-8")

    (workflow_dir / "tests.yml").write_text(VALID_WORKFLOW_CONTENT, encoding="utf-8")


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

    def test_json_output_is_valid(self) -> None:
        result = _run_health_tool(["--json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        parsed = json.loads(result.stdout)
        self.assertIsInstance(parsed, dict)
        self.assertIn("overall", parsed)
        self.assertIn("tools", parsed)
        self.assertIn("workflow", parsed)
        self.assertIn("fragments", parsed)

    def test_text_output_contains_overall(self) -> None:
        result = _run_health_tool([])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics CI health:", result.stdout)
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

    def test_markdown_report_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_health.md"
            result = _run_health_tool(["--check", "--markdown-output", str(output_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Support metrics CI health", content)
            self.assertIn("- overall:", content)
            self.assertIn("not gameplay validation", content)


if __name__ == "__main__":
    unittest.main()
