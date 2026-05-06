from __future__ import annotations

from pathlib import Path
from typing import Any
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "tests.yml"
README_PATH = ROOT / "README.md"
ANALYZE_TOOL_PATH = ROOT / "tools" / "analyze_run_metrics_history.py"


class SupportMetricsCIWorkflowStaticTests(unittest.TestCase):
    def _read_workflow_content(self) -> str:
        return WORKFLOW_PATH.read_text(encoding="utf-8")

    def _load_workflow_yaml_if_available(self) -> dict[str, Any] | None:
        content = self._read_workflow_content()
        try:
            import yaml  # type: ignore[import-not-found]
        except Exception:
            return None

        parsed = yaml.safe_load(content)
        self.assertIsInstance(parsed, dict, msg="Workflow YAML should parse to a mapping")
        return parsed

    def _get_workflow_steps(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        jobs = parsed.get("jobs", {})
        self.assertIsInstance(jobs, dict, msg="Workflow jobs must be a mapping")

        tests_job = jobs.get("tests", {})
        self.assertIsInstance(tests_job, dict, msg="Workflow tests job must be a mapping")

        steps = tests_job.get("steps", [])
        self.assertIsInstance(steps, list, msg="Workflow steps must be a list")

        step_dicts = [step for step in steps if isinstance(step, dict)]
        self.assertGreater(len(step_dicts), 0, msg="Workflow steps list is empty")
        return step_dicts

    def _get_named_step(self, steps: list[dict[str, Any]], name: str) -> dict[str, Any]:
        for step in steps:
            if step.get("name") == name:
                return step
        self.fail("Missing workflow step: %s" % name)

    def test_workflow_file_exists(self) -> None:
        self.assertTrue(WORKFLOW_PATH.exists(), msg=f"Missing workflow: {WORKFLOW_PATH}")

    def test_workflow_is_yaml_parsable_when_pyyaml_is_available(self) -> None:
        parsed = self._load_workflow_yaml_if_available()
        if parsed is None:
            content = self._read_workflow_content()
            self.assertIn("jobs:", content)
            self.assertIn("steps:", content)
            return
        self.assertIn("jobs", parsed)

    def test_workflow_runs_unittest_discover(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn('py -m unittest discover -s tests -p "test_*.py"', content)
        self.assertIn("Validate support metrics CI fragments", content)
        self.assertIn("py tools/check_support_metrics_ci_fragments.py --validate", content)
        self.assertIn("Validate support metrics CI contract audit", content)
        self.assertIn("py tools/audit_support_metrics_ci_contract.py --check", content)
        self.assertIn("--markdown-output \"$env:SUPPORT_METRICS_CONTRACT_AUDIT_REPORT_PATH\"", content)
        self.assertIn("Validate support metrics CI health", content)
        self.assertIn("py tools/check_support_metrics_ci_health.py --check", content)
        self.assertIn("--markdown-output artifacts/support_metrics_ci_health.md", content)

    def test_workflow_support_metrics_check_is_optional_and_non_blocking_by_default(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("tools/write_support_metrics_ci_summary.py", content)
        self.assertNotIn("tools/analyze_run_metrics_history.py", content)
        self.assertIn("--ci-check", content)
        self.assertIn("GITHUB_STEP_SUMMARY", content)
        self.assertIn(
            'Get-Content artifacts/support_metrics_ci_health.md | Add-Content -Path $env:GITHUB_STEP_SUMMARY',
            content,
        )
        self.assertNotIn("ConvertFrom-Json", content)
        self.assertNotIn("--fail-on-regression", content)

    def test_workflow_generates_markdown_report_and_uploads_artifact(self) -> None:
        content = self._read_workflow_content()
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
            "Upload support metrics CI contract audit artifact",
            content,
        )
        self.assertIn(
            "tests/fixtures/support_metrics_contract/recent_complete.jsonl",
            content,
        )
        self.assertIn("artifacts/support_metrics_smoke_report.md", content)
        self.assertIn("support-metrics-smoke-report", content)
        self.assertIn("artifacts/support_metrics_report.md", content)
        self.assertIn("artifacts/support_metrics_ci_health.md", content)
        self.assertIn("support-metrics-ci-health", content)
        self.assertIn("artifacts/support_metrics_ci_contract_audit.md", content)
        self.assertIn("support-metrics-ci-contract-audit", content)
        self.assertIn("SUPPORT_METRICS_CONTRACT_AUDIT_REPORT_PATH", content)
        self.assertIn("Upload support metrics CI health artifact", content)
        self.assertIn("if: always()", content)
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

    def test_workflow_step_structure_keeps_expected_paths(self) -> None:
        parsed = self._load_workflow_yaml_if_available()
        if parsed is None:
            content = self._read_workflow_content()
            self.assertIn("outputs/ci/support_metrics_baseline.jsonl", content)
            self.assertIn("tests/fixtures/support_metrics_contract/recent_complete.jsonl", content)
            return

        steps = self._get_workflow_steps(parsed)
        step_names = [str(step.get("name", "")) for step in steps]
        self.assertIn("Run unit tests", step_names)
        self.assertIn("Validate support metrics CI fragments", step_names)
        self.assertIn("Validate support metrics CI contract audit", step_names)
        self.assertIn("Validate support metrics CI health", step_names)
        self.assertIn("Smoke test support metrics CI summary (technical fixtures)", step_names)
        self.assertIn("Optional runtime support metrics CI check (outputs/ci)", step_names)

        smoke_step = self._get_named_step(steps, "Smoke test support metrics CI summary (technical fixtures)")
        smoke_run = str(smoke_step.get("run", ""))
        self.assertIn("recent_complete.jsonl", smoke_run)
        self.assertNotIn("$env:SUPPORT_METRICS_BASELINE_PATH", smoke_run)
        self.assertNotIn("$env:SUPPORT_METRICS_CURRENT_PATH", smoke_run)

        runtime_step = self._get_named_step(steps, "Optional runtime support metrics CI check (outputs/ci)")
        runtime_run = str(runtime_step.get("run", ""))
        self.assertIn("$env:SUPPORT_METRICS_BASELINE_PATH", runtime_run)
        self.assertIn("$env:SUPPORT_METRICS_CURRENT_PATH", runtime_run)
        self.assertNotIn("recent_complete.jsonl", runtime_run)

        smoke_artifact = self._get_named_step(steps, "Upload support metrics smoke report artifact (technical fixtures)")
        runtime_artifact = self._get_named_step(steps, "Upload support metrics runtime report artifact (optional)")
        health_artifact = self._get_named_step(steps, "Upload support metrics CI health artifact")
        contract_audit_artifact = self._get_named_step(steps, "Upload support metrics CI contract audit artifact")

        self.assertEqual(smoke_artifact.get("with", {}).get("if-no-files-found"), "error")
        self.assertEqual(health_artifact.get("with", {}).get("if-no-files-found"), "error")
        self.assertEqual(contract_audit_artifact.get("with", {}).get("if-no-files-found"), "error")
        self.assertEqual(runtime_artifact.get("with", {}).get("if-no-files-found"), "ignore")

    def test_workflow_keeps_smoke_and_runtime_paths_separated(self) -> None:
        content = self._read_workflow_content()
        self.assertIn("SUPPORT_METRICS_BASELINE_PATH: outputs/ci/support_metrics_baseline.jsonl", content)
        self.assertIn("SUPPORT_METRICS_CURRENT_PATH: outputs/ci/support_metrics_current.jsonl", content)
        self.assertIn("SUPPORT_METRICS_REPORT_PATH: artifacts/support_metrics_report.md", content)
        self.assertIn("SUPPORT_METRICS_CONTRACT_AUDIT_REPORT_PATH: artifacts/support_metrics_ci_contract_audit.md", content)
        self.assertIn("--baseline tests/fixtures/support_metrics_contract/recent_complete.jsonl", content)
        self.assertIn("--current tests/fixtures/support_metrics_contract/recent_complete.jsonl", content)
        self.assertIn("--baseline \"$env:SUPPORT_METRICS_BASELINE_PATH\"", content)
        self.assertIn("--current \"$env:SUPPORT_METRICS_CURRENT_PATH\"", content)
        self.assertIn("Get-Content \"$env:SUPPORT_METRICS_CONTRACT_AUDIT_REPORT_PATH\" | Add-Content -Path $env:GITHUB_STEP_SUMMARY", content)
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
        self.assertIn("smoke/runtime-skip/error/local/health", content)
        self.assertIn("Support metrics CI fragments maintenance", content)
        self.assertIn("check_support_metrics_ci_fragments.py", content)
        self.assertIn("py tools/check_support_metrics_ci_fragments.py --validate", content)
        self.assertIn("py tools/check_support_metrics_ci_fragments.py --list", content)
        self.assertIn("Support metrics CI health check", content)
        self.assertIn("check_support_metrics_ci_health.py --check", content)
        self.assertIn("la CI GitHub Actions execute aussi `py tools/check_support_metrics_ci_health.py --check`", content)
        self.assertIn(
            "verifie aussi que l'index README `Support metrics tools index` reste documente",
            content,
        )
        self.assertIn("verifie aussi le contrat `--help` des outils support metrics", content)
        self.assertIn("Support metrics CI contract audit", content)
        self.assertIn("py tools/audit_support_metrics_ci_contract.py --check", content)
        self.assertIn("la CI GitHub Actions execute aussi `py tools/audit_support_metrics_ci_contract.py --check`", content)
        self.assertIn("Support metrics CI contract audit artifact", content)
        self.assertIn("support-metrics-ci-contract-audit", content)
        self.assertIn("artifacts/support_metrics_ci_contract_audit.md", content)
        self.assertIn("Support metrics CI health artifact", content)
        self.assertIn("artifacts/support_metrics_ci_health.md", content)
        self.assertIn("support-metrics-ci-health", content)
        self.assertIn("health_summary_expected_fragments.txt", content)
        self.assertIn("health_report_expected_fragments.txt", content)
        self.assertIn("pas la validation gameplay", content)
        self.assertIn("Support metrics tools index", content)
        self.assertIn("analyze_run_metrics_history.py", content)
        self.assertIn("write_support_metrics_ci_summary.py", content)
        self.assertIn("simulate_support_metrics_ci.py", content)
        self.assertIn("check_support_metrics_ci_fragments.py", content)
        self.assertIn("check_support_metrics_ci_health.py", content)
        self.assertIn("CI/debug only", content)
        self.assertIn("not gameplay validation", content)
        self.assertIn("runtime report optional", content)
        self.assertIn("no --fail-on-regression by default", content)
        self.assertIn("contrat CLI help", content)
        self.assertIn("tests/fixtures/support_metrics_cli_help_expected.json", content)
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
