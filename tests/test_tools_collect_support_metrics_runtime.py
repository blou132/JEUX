from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "collect_support_metrics_runtime.py"


def _run_tool(extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class CollectSupportMetricsRuntimeToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--mode", result.stdout)
        self.assertIn("--runs", result.stdout)
        self.assertIn("--seed-start", result.stdout)
        self.assertIn("--output", result.stdout)
        self.assertIn("--godot-bin", result.stdout)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--project-path", result.stdout)
        self.assertIn("--history-path", result.stdout)

    def test_godot_absent_returns_non_zero_and_clear_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    "__missing_godot_binary_for_collect_runtime_tests__",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            merged_output = result.stdout + "\n" + result.stderr
            self.assertIn("Godot binary not found", merged_output)
            self.assertTrue(output_path.parent.exists())

    def test_dry_run_succeeds_without_godot(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "baseline",
                "--runs",
                "2",
                "--seed-start",
                "2000",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("DRY-RUN: planned commands", result.stdout)
        self.assertIn("--support-metrics-seed 2000", result.stdout)
        self.assertIn("--support-metrics-seed 2001", result.stdout)

    def test_mode_baseline_uses_expected_default_output_path(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "baseline",
                "--runs",
                "1",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("outputs/ci/support_metrics_baseline.jsonl", normalized_output)

    def test_mode_current_uses_expected_default_output_path(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "current",
                "--runs",
                "1",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("outputs/ci/support_metrics_current.jsonl", normalized_output)

    def test_output_directory_is_created_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "ci" / "runtime_metrics.jsonl"
            self.assertFalse(output_path.parent.exists())
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    "__missing_godot_binary_for_collect_runtime_tests__",
                    "--dry-run",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.parent.exists())


if __name__ == "__main__":
    unittest.main()
