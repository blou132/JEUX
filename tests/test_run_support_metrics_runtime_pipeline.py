from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "run_support_metrics_runtime_pipeline.py"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_contract"


def _fixture_path(file_name: str) -> Path:
    return FIXTURES_DIR / file_name


def _run_tool(extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class RunSupportMetricsRuntimePipelineToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--runs", result.stdout)
        self.assertIn("--seed-start", result.stdout)
        self.assertIn("--baseline-output", result.stdout)
        self.assertIn("--current-output", result.stdout)
        self.assertIn("--report-output", result.stdout)
        self.assertIn("--decision-output", result.stdout)
        self.assertIn("--decision-json-output", result.stdout)
        self.assertIn("--min-runs", result.stdout)
        self.assertIn("--godot-bin", result.stdout)
        self.assertIn("--objective", result.stdout)
        self.assertIn("--export-on-quit", result.stdout)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--skip-collect", result.stdout)
        self.assertIn("--skip-decision", result.stdout)
        self.assertIn("--strict", result.stdout)

    def test_dry_run_returns_zero(self) -> None:
        result = _run_tool(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("DRY-RUN: planned commands", result.stdout)

    def test_dry_run_displays_collect_baseline_and_current_commands(self) -> None:
        result = _run_tool(["--dry-run", "--runs", "2", "--seed-start", "1000"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("collect 1:", normalized_output)
        self.assertIn("--mode baseline", normalized_output)
        self.assertIn("collect 2:", normalized_output)
        self.assertIn("--mode current", normalized_output)
        self.assertIn("collect_support_metrics_runtime.py", normalized_output)
        self.assertIn("- validate:", normalized_output)
        self.assertIn("- analyze:", normalized_output)
        self.assertIn("- decision:", normalized_output)
        self.assertIn("decide_support_metrics_runtime_tuning.py", normalized_output)
        self.assertIn("--min-runs 5", normalized_output)

    def test_dry_run_objective_shows_collect_and_forwarded_runtime_flags(self) -> None:
        result = _run_tool(
            ["--dry-run", "--runs", "2", "--seed-start", "1000", "--objective", "rally_champion"]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("collect 1:", normalized_output)
        self.assertIn("--mode baseline", normalized_output)
        self.assertIn("collect 2:", normalized_output)
        self.assertIn("--mode current", normalized_output)
        self.assertIn("--objective rally_champion", normalized_output)
        self.assertIn("--support-metrics-objective rally_champion", normalized_output)

    def test_dry_run_export_on_quit_shows_collect_and_forwarded_runtime_flags(self) -> None:
        result = _run_tool(
            ["--dry-run", "--runs", "2", "--seed-start", "1000", "--export-on-quit"]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("collect 1:", normalized_output)
        self.assertIn("--mode baseline", normalized_output)
        self.assertIn("collect 2:", normalized_output)
        self.assertIn("--mode current", normalized_output)
        self.assertIn("--export-on-quit", normalized_output)
        self.assertIn("--support-metrics-export-on-quit", normalized_output)

    def test_dry_run_objective_and_export_on_quit_are_forwarded_to_both_collects(self) -> None:
        result = _run_tool(
            [
                "--dry-run",
                "--runs",
                "2",
                "--seed-start",
                "1000",
                "--objective",
                "rally_champion",
                "--export-on-quit",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertGreaterEqual(
            normalized_output.count("--support-metrics-objective rally_champion"),
            2,
        )
        self.assertGreaterEqual(
            normalized_output.count("--support-metrics-export-on-quit"),
            2,
        )

    def test_dry_run_skip_collect_remains_compatible_with_objective_export_on_quit(self) -> None:
        result = _run_tool(
            ["--dry-run", "--skip-collect", "--objective", "rally_champion", "--export-on-quit"]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("collect: skipped (--skip-collect)", normalized_output)
        self.assertIn("- validate:", normalized_output)
        self.assertIn("- analyze:", normalized_output)
        self.assertIn("- decision:", normalized_output)

    def test_dry_run_skip_decision_remains_compatible_with_objective_export_on_quit(self) -> None:
        result = _run_tool(
            ["--dry-run", "--skip-decision", "--objective", "rally_champion", "--export-on-quit"]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("--support-metrics-objective rally_champion", normalized_output)
        self.assertIn("--support-metrics-export-on-quit", normalized_output)
        self.assertIn("decision: skipped (--skip-decision)", normalized_output)

    def test_skip_collect_with_missing_files_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "missing_baseline.jsonl"
            current_path = Path(tmpdir) / "missing_current.jsonl"
            report_path = Path(tmpdir) / "support_metrics_runtime_comparison.md"
            result = _run_tool(
                [
                    "--skip-collect",
                    "--baseline-output",
                    str(baseline_path),
                    "--current-output",
                    str(current_path),
                    "--report-output",
                    str(report_path),
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + "\n" + result.stderr
        self.assertIn("skip-collect requires existing runtime files", combined)

    def test_skip_collect_with_valid_fixtures_generates_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_runtime_comparison.md"
            decision_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_runtime_decision.md"
            result = _run_tool(
                [
                    "--skip-collect",
                    "--baseline-output",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current-output",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--report-output",
                    str(report_path),
                    "--decision-output",
                    str(decision_path),
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(decision_path.exists())
            content = report_path.read_text(encoding="utf-8")
            self.assertIn("# Run Metrics History Analysis", content)
            self.assertIn("## Comparison", content)
            decision_content = decision_path.read_text(encoding="utf-8")
            self.assertIn("- decision:", decision_content)
            self.assertIn("- reasons:", decision_content)
            self.assertIn("- gameplay_change_allowed: false", decision_content)

    def test_min_runs_is_forwarded_to_decision_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            decision_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_runtime_decision.md"
            result = _run_tool(
                [
                    "--skip-collect",
                    "--baseline-output",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current-output",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--decision-output",
                    str(decision_path),
                    "--min-runs",
                    "7",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(decision_path.exists())
            decision_content = decision_path.read_text(encoding="utf-8")
            self.assertIn("- minimum required runs per side: 7", decision_content)
            self.assertIn("- decision: collect_more_runs", decision_content)

    def test_skip_decision_disables_decision_report_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_runtime_comparison.md"
            decision_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_runtime_decision.md"
            result = _run_tool(
                [
                    "--skip-collect",
                    "--skip-decision",
                    "--baseline-output",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current-output",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--report-output",
                    str(report_path),
                    "--decision-output",
                    str(decision_path),
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertFalse(decision_path.exists())
            self.assertNotIn("Decision report written to", result.stdout)

    def test_missing_godot_without_dry_run_or_skip_collect_returns_error(self) -> None:
        result = _run_tool(
            [
                "--godot-bin",
                "__missing_godot_binary_for_runtime_pipeline_tests__",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + "\n" + result.stderr
        self.assertIn("Godot binary not found", combined)


if __name__ == "__main__":
    unittest.main()
