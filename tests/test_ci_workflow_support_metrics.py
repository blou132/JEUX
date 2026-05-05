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
        self.assertIn("--ci-check", content)
        self.assertNotIn("--fail-on-regression", content)
        self.assertIn("Support metrics CI check skipped: missing exports.", content)
        self.assertIn("Support metrics exports not found; optional check skipped.", content)
        self.assertIn("GITHUB_STEP_SUMMARY", content)

    def test_workflow_generates_markdown_report_and_uploads_artifact(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("--format markdown", content)
        self.assertIn("artifacts/support_metrics_report.md", content)
        self.assertIn("actions/upload-artifact@v4", content)
        self.assertIn("if-no-files-found: ignore", content)
        self.assertIn("support-metrics-report", content)
        self.assertIn("## Support metrics report", content)

    def test_readme_documents_optional_ci_mode(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("CI standard = tests unitaires", content)
        self.assertIn("CI support metrics = debug/observation", content)
        self.assertIn("absence d'exports = pas d'echec", content)
        self.assertIn("--ci-check --fail-on-regression", content)
        self.assertIn("support-metrics-report", content)
        self.assertIn("artifact", content)
        self.assertIn("Summary", content)

    def test_support_metrics_ci_check_block_is_still_present_in_tool(self) -> None:
        content = ANALYZE_TOOL_PATH.read_text(encoding="utf-8")
        self.assertIn("def build_support_metrics_ci_check(", content)
        self.assertIn("support_metrics_ci_check", content)


if __name__ == "__main__":
    unittest.main()
