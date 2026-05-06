from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "tests.yml"
README_PATH = ROOT / "README.md"
ANALYZE_TOOL_PATH = ROOT / "tools" / "analyze_run_metrics_history.py"


class SupportMetricsCIWorkflowStaticTests(unittest.TestCase):
    def test_workflow_file_exists(self) -> None:
        self.assertTrue(WORKFLOW_PATH.exists(), msg=f"Missing workflow: {WORKFLOW_PATH}")

    def test_workflow_runs_unittest_discover(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn('py -m unittest discover -s tests -p "test_*.py"', content)

    def test_workflow_support_metrics_check_is_optional_and_non_blocking_by_default(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("tools/write_support_metrics_ci_summary.py", content)
        self.assertNotIn("tools/analyze_run_metrics_history.py", content)
        self.assertIn("--ci-check", content)
        self.assertIn("GITHUB_STEP_SUMMARY", content)
        self.assertNotIn("ConvertFrom-Json", content)
        self.assertNotIn("--fail-on-regression", content)

    def test_workflow_generates_markdown_report_and_uploads_artifact(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Smoke test support metrics CI summary (technical fixtures)",
            content,
        )
        self.assertIn(
            "Upload support metrics smoke report artifact (technical fixtures)",
            content,
        )
        self.assertIn(
            "Optional runtime support metrics CI check (outputs/ci)",
            content,
        )
        self.assertIn(
            "Upload support metrics runtime report artifact (optional)",
            content,
        )
        self.assertIn(
            "tests/fixtures/support_metrics_contract/recent_complete.jsonl",
            content,
        )
        self.assertIn("artifacts/support_metrics_smoke_report.md", content)
        self.assertIn("support-metrics-smoke-report", content)
        self.assertIn("artifacts/support_metrics_report.md", content)
        self.assertIn("actions/upload-artifact@v4", content)
        self.assertIn("if-no-files-found: ignore", content)
        self.assertIn("if-no-files-found: error", content)
        self.assertIn("support-metrics-report", content)
        self.assertIn("--artifact-name \"support-metrics-report\"", content)
        self.assertIn("--artifact-name \"support-metrics-smoke-report\"", content)
        self.assertIn("--report-mode \"smoke\"", content)
        self.assertIn("--report-mode \"runtime\"", content)
        self.assertIn("--input-label \"fixtures:recent_complete.jsonl\"", content)
        self.assertIn("--compare-input-label \"fixtures:recent_complete.jsonl\"", content)

    def test_workflow_keeps_smoke_and_runtime_paths_separated(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("SUPPORT_METRICS_BASELINE_PATH: outputs/ci/support_metrics_baseline.jsonl", content)
        self.assertIn("SUPPORT_METRICS_CURRENT_PATH: outputs/ci/support_metrics_current.jsonl", content)
        self.assertIn("SUPPORT_METRICS_REPORT_PATH: artifacts/support_metrics_report.md", content)
        self.assertIn("--baseline tests/fixtures/support_metrics_contract/recent_complete.jsonl", content)
        self.assertIn("--current tests/fixtures/support_metrics_contract/recent_complete.jsonl", content)
        self.assertIn("--baseline \"$env:SUPPORT_METRICS_BASELINE_PATH\"", content)
        self.assertIn("--current \"$env:SUPPORT_METRICS_CURRENT_PATH\"", content)
        self.assertIn("--report-output artifacts/support_metrics_smoke_report.md", content)
        self.assertIn("--report-output \"$env:SUPPORT_METRICS_REPORT_PATH\"", content)
        self.assertIn("--input-label \"$env:SUPPORT_METRICS_BASELINE_PATH\"", content)
        self.assertIn("--compare-input-label \"$env:SUPPORT_METRICS_CURRENT_PATH\"", content)

    def test_readme_documents_optional_ci_mode(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("CI standard = tests unitaires", content)
        self.assertIn("CI support metrics = debug/observation", content)
        self.assertIn("absence d'exports = pas d'echec", content)
        self.assertIn("--ci-check --fail-on-regression", content)
        self.assertIn("support-metrics-report", content)
        self.assertIn("artifact", content)
        self.assertIn("Summary", content)
        self.assertIn("status compact", content)
        self.assertIn("script Python", content)
        self.assertIn("fail-safe", content)
        self.assertIn("--strict", content)
        self.assertIn("CI support metrics reports", content)
        self.assertIn("support-metrics-smoke-report", content)
        self.assertIn("support-metrics-report", content)
        self.assertIn("Support metrics reports index", content)
        self.assertIn("Smoke report vs runtime report", content)
        self.assertIn("smoke OK != gameplay OK", content)
        self.assertIn("runtime absent != echec gameplay", content)
        self.assertIn("CI report output contract", content)
        self.assertIn("support_metrics_ci_outputs", content)
        self.assertIn("snapshots par fragments", content)
        self.assertIn("Support metrics CI fragments maintenance", content)
        self.assertIn("check_support_metrics_ci_fragments.py", content)
        self.assertIn("py tools/check_support_metrics_ci_fragments.py --validate", content)
        self.assertIn("py tools/check_support_metrics_ci_fragments.py --list", content)
        self.assertIn("smoke", content)
        self.assertIn("runtime", content)

    def test_support_metrics_ci_check_block_is_still_present_in_tool(self) -> None:
        content = ANALYZE_TOOL_PATH.read_text(encoding="utf-8")
        self.assertIn("def build_support_metrics_ci_check(", content)
        self.assertIn("support_metrics_ci_check", content)
        self.assertIn("def build_support_metrics_report_provenance(", content)
        self.assertIn("support_metrics_report_provenance", content)


if __name__ == "__main__":
    unittest.main()
