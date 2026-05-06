from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.support_metrics_output_fragments import assert_expected_fragments_present


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "simulate_support_metrics_ci.py"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_contract"
OUTPUT_CONTRACT_FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_ci_outputs"


def _run_simulation(
    baseline_path: Path,
    current_path: Path,
    output_dir: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--baseline",
        str(baseline_path),
        "--current",
        str(current_path),
        "--output-dir",
        str(output_dir),
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

if fmt == "markdown":
    output_path = _arg_value("--output")
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text("# Fake report\\n", encoding="utf-8")
    raise SystemExit(0)

if fmt == "json":
    if mode == "invalid_json":
        print("{{invalid_json")
        raise SystemExit(0)
    print(json.dumps({{"support_metrics_regression": {{"regression_state": "stable"}}}}))
    raise SystemExit(0)

raise SystemExit(1)
"""
    path.write_text(content, encoding="utf-8")


class SimulateSupportMetricsCIToolTests(unittest.TestCase):
    def test_simulation_help_exposes_report_mode_option(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--report-mode", result.stdout)

    def test_simulation_with_recent_fixtures_generates_report_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "simulation"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_simulation(baseline, current, output_dir)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            report_path = output_dir / "artifacts" / "support_metrics_report.md"
            summary_path = output_dir / "artifacts" / "github_step_summary.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertIn("# Run Metrics History Analysis", report_path.read_text(encoding="utf-8"))

            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("Support metrics CI status", summary_text)
            self.assertIn("- status: passed", summary_text)
            self.assertIn("- artifact: support-metrics-report", summary_text)
            self.assertIn("- source: local simulation", summary_text)
            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("## Report provenance", report_text)
            self.assertIn("- mode: local", report_text)

    def test_simulation_missing_exports_is_skipped_and_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "simulation"
            baseline = Path(tmpdir) / "missing_baseline.jsonl"
            current = Path(tmpdir) / "missing_current.jsonl"

            result = _run_simulation(baseline, current, output_dir)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            report_path = output_dir / "artifacts" / "support_metrics_report.md"
            summary_path = output_dir / "artifacts" / "github_step_summary.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertIn("optional check skipped", report_path.read_text(encoding="utf-8"))
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("- status: skipped", summary_text)
            self.assertIn("- blocking: no", summary_text)

    def test_simulation_invalid_json_is_warning_and_non_blocking_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "simulation"
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="invalid_json")
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_simulation(
                baseline,
                current,
                output_dir,
                extra_args=["--analyze-script", str(fake_analyze_path)],
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            report_path = output_dir / "artifacts" / "support_metrics_report.md"
            summary_path = output_dir / "artifacts" / "github_step_summary.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertIn("Support metrics CI check failed", report_path.read_text(encoding="utf-8"))

            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("Support metrics CI status", summary_text)
            self.assertIn("- status: warning", summary_text)
            self.assertIn("- reason: analysis failed", summary_text)
            self.assertIn("- blocking: no", summary_text)

    def test_simulation_invalid_json_with_strict_mode_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "simulation"
            fake_analyze_path = Path(tmpdir) / "fake_analyze.py"
            _write_fake_analyze_script(fake_analyze_path, mode="invalid_json")
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_simulation(
                baseline,
                current,
                output_dir,
                extra_args=["--analyze-script", str(fake_analyze_path), "--strict"],
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((output_dir / "artifacts" / "support_metrics_report.md").exists())
            self.assertTrue((output_dir / "artifacts" / "github_step_summary.md").exists())

    def test_simulation_default_mode_stays_non_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "simulation"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "incoherent_export.jsonl"

            result = _run_simulation(baseline, current, output_dir)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_simulation_artifact_path_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "custom_output"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_simulation(baseline, current, output_dir)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            report_path = output_dir / "artifacts" / "support_metrics_report.md"
            summary_path = output_dir / "artifacts" / "github_step_summary.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())

    def test_local_simulation_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "simulation"
            baseline = FIXTURES_DIR / "recent_complete.jsonl"
            current = FIXTURES_DIR / "recent_complete.jsonl"

            result = _run_simulation(baseline, current, output_dir)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            report_path = output_dir / "artifacts" / "support_metrics_report.md"
            summary_path = output_dir / "artifacts" / "github_step_summary.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())

            summary_text = summary_path.read_text(encoding="utf-8")
            report_text = report_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                summary_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "local_simulation_summary_expected_fragments.txt",
            )
            assert_expected_fragments_present(
                self,
                report_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "local_simulation_report_expected_fragments.txt",
            )


if __name__ == "__main__":
    unittest.main()
