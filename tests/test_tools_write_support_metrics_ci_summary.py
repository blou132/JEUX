from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "write_support_metrics_ci_summary.py"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_contract"


def _write_jsonl(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _run_ci_summary_tool(
    baseline_path: Path,
    current_path: Path,
    report_path: Path,
    summary_path: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--baseline",
        str(baseline_path),
        "--current",
        str(current_path),
        "--report-output",
        str(report_path),
        "--step-summary",
        str(summary_path),
        "--artifact-name",
        "support-metrics-report",
        "--ci-check",
    ]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _write_fake_analyze_script(path: Path, mode: str) -> None:
    content = f"""from __future__ import annotations
import json
import sys
from pathlib import Path

def _arg_value(name: str) -> str:
    if name in sys.argv:
        index = sys.argv.index(name)
        if index + 1 < len(sys.argv):
            return sys.argv[index + 1]
    return ""

mode = {mode!r}
fmt = _arg_value("--format")

if mode == "non_zero":
    print("simulated failure")
    raise SystemExit(2)

if fmt == "markdown":
    output_path = _arg_value("--output")
    if mode == "markdown_non_zero":
        print("markdown generation failed")
        raise SystemExit(3)
    if mode == "markdown_no_output":
        raise SystemExit(0)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text("# Fake report\\n\\ncontent\\n", encoding="utf-8")
    raise SystemExit(0)

if fmt == "json":
    if mode == "json_non_zero":
        print("json generation failed")
        raise SystemExit(4)
    if mode == "invalid_json":
        print("{{invalid_json")
        raise SystemExit(0)
    if mode == "missing_regression_state":
        print(json.dumps({{"support_metrics_regression": {{}}}}))
        raise SystemExit(0)
    if mode == "missing_regression_block":
        print(json.dumps({{"foo": "bar"}}))
        raise SystemExit(0)
    print(json.dumps({{"support_metrics_regression": {{"regression_state": "stable"}}}}))
    raise SystemExit(0)

print("unsupported format")
raise SystemExit(1)
"""
    path.write_text(content, encoding="utf-8")


class WriteSupportMetricsCISummaryToolTests(unittest.TestCase):
    def test_help_exposes_strict_and_analyze_script_options(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--strict", result.stdout)
        self.assertIn("--analyze-script", result.stdout)

    def test_exports_present_stable_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(baseline, current, report_path, summary_path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())

            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("## Support metrics CI status", summary_text)
            self.assertIn("- status: passed", summary_text)
            self.assertIn("- blocking: no", summary_text)
            self.assertIn("- artifact: support-metrics-report", summary_text)
            self.assertIn("## Support metrics report", summary_text)
            self.assertIn("# Run Metrics History Analysis", summary_text)

    def test_exports_present_changed_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline.jsonl"
            current_path = Path(tmpdir) / "current.jsonl"
            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            _write_jsonl(
                baseline_path,
                [
                    json.dumps(
                        {
                            "export_id": "base_gate",
                            "objective_id": "support_gate",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "support_gate_run_attempts": 6,
                            "support_gate_run_success": 4,
                            "support_gate_run_success_rate": 0.66,
                            "support_gate_run_available_ratio": 0.50,
                        }
                    ),
                    json.dumps(
                        {
                            "export_id": "base_champ",
                            "objective_id": "rally_champion",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "champion_support_run_attempts": 5,
                            "champion_support_run_success": 3,
                            "champion_support_run_success_rate": 0.60,
                            "champion_support_attempts_total": 5,
                            "champion_support_success_total": 3,
                            "champion_support_unavailable_total": 1,
                            "champion_support_cooldown_blocked_total": 1,
                            "champion_support_completed_total": 1,
                            "champion_support_failed_total": 0,
                        }
                    ),
                ],
            )
            _write_jsonl(
                current_path,
                [
                    json.dumps(
                        {
                            "export_id": "curr_gate",
                            "objective_id": "support_gate",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "support_gate_run_attempts": 6,
                            "support_gate_run_success": 3,
                            "support_gate_run_success_rate": 0.50,
                            "support_gate_run_available_ratio": 0.50,
                        }
                    ),
                    json.dumps(
                        {
                            "export_id": "curr_champ",
                            "objective_id": "rally_champion",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "champion_support_run_attempts": 5,
                            "champion_support_run_success": 3,
                            "champion_support_run_success_rate": 0.60,
                            "champion_support_attempts_total": 5,
                            "champion_support_success_total": 3,
                            "champion_support_unavailable_total": 1,
                            "champion_support_cooldown_blocked_total": 1,
                            "champion_support_completed_total": 1,
                            "champion_support_failed_total": 0,
                        }
                    ),
                ],
            )

            result = _run_ci_summary_tool(baseline_path, current_path, report_path, summary_path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: changed", summary_text)

    def test_exports_present_warning_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "incoherent_export.jsonl"

            result = _run_ci_summary_tool(baseline, current, report_path, summary_path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: warning", summary_text)

    def test_exports_absent_is_skipped_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline = Path(tmpdir) / "missing_baseline.jsonl"
            current = Path(tmpdir) / "missing_current.jsonl"
            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"

            result = _run_ci_summary_tool(baseline, current, report_path, summary_path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("Support metrics exports not found; optional check skipped.", report_text)

            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: skipped", summary_text)
            self.assertIn("- reason: exports baseline/current not found", summary_text)
            self.assertIn("- blocking: no", summary_text)

    def test_artifact_path_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "nested" / "artifacts" / "support_metrics_report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(baseline, current, report_path, summary_path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertIn("Run Metrics History Analysis", report_path.read_text(encoding="utf-8"))

    def test_default_mode_is_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "incoherent_export.jsonl"

            result = _run_ci_summary_tool(baseline, current, report_path, summary_path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_json_invalid_is_warning_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="invalid_json")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)
            self.assertIn("- blocking: no", summary_text)
            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("Support metrics CI check failed", report_text)
            self.assertIn("- reason: analysis failed", report_text)
            self.assertIn("- blocking: no", report_text)

    def test_analyze_non_zero_is_warning_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="non_zero")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("- status: warning", summary_path.read_text(encoding="utf-8"))
            self.assertTrue(report_path.exists())

    def test_markdown_analysis_failure_generates_minimal_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="markdown_non_zero")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("Support metrics CI check failed", report_text)
            self.assertIn("- reason: analysis failed", report_text)
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)

    def test_json_analysis_failure_generates_minimal_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="json_non_zero")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("Support metrics CI check failed", report_text)
            self.assertIn("- reason: analysis failed", report_text)
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)

    def test_missing_regression_state_is_warning_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="missing_regression_state")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)
            self.assertTrue(report_path.exists())

    def test_missing_regression_block_is_warning_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="missing_regression_block")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("- status: warning", summary_path.read_text(encoding="utf-8"))

    def test_strict_mode_is_blocking_on_technical_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="non_zero")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path), "--strict"],
            )
            self.assertEqual(result.returncode, 1)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())

    def test_json_invalid_with_strict_mode_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="invalid_json")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path), "--strict"],
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)
            self.assertIn("- blocking: no", summary_text)

    def test_markdown_report_missing_is_warning_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="markdown_no_output")

            report_path = Path(tmpdir) / "artifacts" / "report.md"
            summary_path = Path(tmpdir) / "summary.md"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_ci_summary_tool(
                baseline,
                current,
                report_path,
                summary_path,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)


if __name__ == "__main__":
    unittest.main()
