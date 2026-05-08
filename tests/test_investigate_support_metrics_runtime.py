from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "investigate_support_metrics_runtime.py"
ANALYZE_SCRIPT = ROOT / "tools" / "analyze_run_metrics_history.py"
DECIDE_SCRIPT = ROOT / "tools" / "decide_support_metrics_runtime_tuning.py"
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


def _generate_runtime_reference_reports(
    baseline_path: Path,
    current_path: Path,
    comparison_path: Path,
    decision_path: Path,
    min_runs: int = 1,
) -> None:
    comparison_result = subprocess.run(
        [
            sys.executable,
            str(ANALYZE_SCRIPT),
            "--input",
            str(baseline_path),
            "--compare-input",
            str(current_path),
            "--report-mode",
            "runtime",
            "--ci-check",
            "--format",
            "markdown",
            "--output",
            str(comparison_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if comparison_result.returncode != 0:
        raise RuntimeError(comparison_result.stdout + "\n" + comparison_result.stderr)

    decision_result = subprocess.run(
        [
            sys.executable,
            str(DECIDE_SCRIPT),
            "--baseline",
            str(baseline_path),
            "--current",
            str(current_path),
            "--min-runs",
            str(min_runs),
            "--markdown-output",
            str(decision_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if decision_result.returncode != 0:
        raise RuntimeError(decision_result.stdout + "\n" + decision_result.stderr)


class InvestigateSupportMetricsRuntimeToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--baseline", result.stdout)
        self.assertIn("--current", result.stdout)
        self.assertIn("--comparison", result.stdout)
        self.assertIn("--decision", result.stdout)
        self.assertIn("--markdown-output", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--check", result.stdout)

    def test_investigation_with_valid_files_returns_json_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            comparison_path = Path(tmpdir) / "comparison.md"
            decision_path = Path(tmpdir) / "decision.md"
            markdown_path = Path(tmpdir) / "investigation.md"
            _generate_runtime_reference_reports(
                baseline_path=_fixture_path("recent_complete.jsonl"),
                current_path=_fixture_path("recent_complete.jsonl"),
                comparison_path=comparison_path,
                decision_path=decision_path,
                min_runs=1,
            )

            result = _run_tool(
                [
                    "--baseline",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--comparison",
                    str(comparison_path),
                    "--decision",
                    str(decision_path),
                    "--markdown-output",
                    str(markdown_path),
                    "--json",
                    "--check",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIsInstance(payload, dict)
            self.assertIn("decision", payload)
            self.assertIn("confidence", payload)
            self.assertIn("support_metrics_final_decision", payload)
            self.assertIn("support_metrics_regression", payload)
            self.assertIn("run_counts", payload)
            self.assertIn("champion_support_success_rate", payload)
            self.assertFalse(payload["gameplay_change_allowed"])
            self.assertTrue(markdown_path.exists())

    def test_decision_investigate_metrics_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            comparison_path = Path(tmpdir) / "comparison.md"
            decision_path = Path(tmpdir) / "decision.md"
            markdown_path = Path(tmpdir) / "investigation.md"
            _generate_runtime_reference_reports(
                baseline_path=_fixture_path("recent_complete.jsonl"),
                current_path=_fixture_path("incoherent_export.jsonl"),
                comparison_path=comparison_path,
                decision_path=decision_path,
                min_runs=1,
            )

            result = _run_tool(
                [
                    "--baseline",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current",
                    str(_fixture_path("incoherent_export.jsonl")),
                    "--comparison",
                    str(comparison_path),
                    "--decision",
                    str(decision_path),
                    "--markdown-output",
                    str(markdown_path),
                    "--json",
                    "--check",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "investigate_metrics")
            self.assertIn("likely_cause", payload)
            self.assertEqual(payload["next_action"], "inspect warning")
            markdown_content = markdown_path.read_text(encoding="utf-8")
            self.assertIn("- decision: investigate_metrics", markdown_content)
            self.assertIn("- gameplay_change_allowed: false", markdown_content)

    def test_missing_decision_file_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            comparison_path = Path(tmpdir) / "comparison.md"
            comparison_path.write_text("# fake comparison\n", encoding="utf-8")
            missing_decision = Path(tmpdir) / "missing_decision.md"
            result = _run_tool(
                [
                    "--baseline",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--comparison",
                    str(comparison_path),
                    "--decision",
                    str(missing_decision),
                    "--check",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn("decision markdown file not found", combined)

    def test_missing_comparison_file_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            decision_path = Path(tmpdir) / "decision.md"
            decision_path.write_text("# fake decision\n", encoding="utf-8")
            missing_comparison = Path(tmpdir) / "missing_comparison.md"
            result = _run_tool(
                [
                    "--baseline",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--comparison",
                    str(missing_comparison),
                    "--decision",
                    str(decision_path),
                    "--check",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn("comparison markdown file not found", combined)

    def test_invalid_json_runtime_file_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_baseline = Path(tmpdir) / "invalid_baseline.jsonl"
            invalid_baseline.write_text("{invalid json line\n", encoding="utf-8")
            current_path = _fixture_path("recent_complete.jsonl")
            comparison_path = Path(tmpdir) / "comparison.md"
            decision_path = Path(tmpdir) / "decision.md"
            comparison_path.write_text(
                "# Run Metrics History Analysis\n\n## Comparison\n- Baseline exports read: 1\n",
                encoding="utf-8",
            )
            decision_path.write_text(
                "# Runtime gameplay decision protocol\n\n"
                "- decision: investigate_metrics\n"
                "- confidence: medium\n"
                "- minimum_runs_met: true\n"
                "- gameplay_change_allowed: false\n"
                "\n## Runs\n"
                "- minimum required runs per side: 1\n"
                "- baseline support_gate runs: 1\n"
                "- current support_gate runs: 1\n"
                "- baseline exports read: 1\n"
                "- current exports read: 1\n"
                "\n## Signals\n"
                "- quality_state: warning\n"
                "- regression_state: warning\n"
                "- reasons: regression_warning\n",
                encoding="utf-8",
            )
            result = _run_tool(
                [
                    "--baseline",
                    str(invalid_baseline),
                    "--current",
                    str(current_path),
                    "--comparison",
                    str(comparison_path),
                    "--decision",
                    str(decision_path),
                    "--check",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn("invalid JSON lines", combined)

    def test_markdown_output_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            comparison_path = Path(tmpdir) / "comparison.md"
            decision_path = Path(tmpdir) / "decision.md"
            markdown_path = Path(tmpdir) / "investigation.md"
            _generate_runtime_reference_reports(
                baseline_path=_fixture_path("recent_complete.jsonl"),
                current_path=_fixture_path("incoherent_export.jsonl"),
                comparison_path=comparison_path,
                decision_path=decision_path,
                min_runs=1,
            )
            result = _run_tool(
                [
                    "--baseline",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current",
                    str(_fixture_path("incoherent_export.jsonl")),
                    "--comparison",
                    str(comparison_path),
                    "--decision",
                    str(decision_path),
                    "--markdown-output",
                    str(markdown_path),
                    "--check",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(markdown_path.exists())
            content = markdown_path.read_text(encoding="utf-8")
            self.assertIn("# Support metrics runtime investigation", content)
            self.assertIn("- decision:", content)
            self.assertIn("- next action:", content)

    def test_gameplay_change_allowed_remains_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            comparison_path = Path(tmpdir) / "comparison.md"
            decision_path = Path(tmpdir) / "decision.md"
            markdown_path = Path(tmpdir) / "investigation.md"
            _generate_runtime_reference_reports(
                baseline_path=_fixture_path("recent_complete.jsonl"),
                current_path=_fixture_path("incoherent_export.jsonl"),
                comparison_path=comparison_path,
                decision_path=decision_path,
                min_runs=1,
            )
            result = _run_tool(
                [
                    "--baseline",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--current",
                    str(_fixture_path("incoherent_export.jsonl")),
                    "--comparison",
                    str(comparison_path),
                    "--decision",
                    str(decision_path),
                    "--markdown-output",
                    str(markdown_path),
                    "--json",
                    "--check",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("gameplay_change_allowed", payload)
            self.assertFalse(payload["gameplay_change_allowed"])


if __name__ == "__main__":
    unittest.main()
