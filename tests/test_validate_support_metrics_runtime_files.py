from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_support_metrics_runtime_files.py"
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


class ValidateSupportMetricsRuntimeFilesToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--baseline", result.stdout)
        self.assertIn("--current", result.stdout)
        self.assertIn("--check", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--verbose", result.stdout)

    def test_valid_baseline_and_current_fixtures_are_ok(self) -> None:
        result = _run_tool(
            [
                "--baseline",
                str(_fixture_path("recent_complete.jsonl")),
                "--current",
                str(_fixture_path("recent_complete.jsonl")),
                "--check",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("- overall: ok", result.stdout)
        self.assertIn("- baseline: ok", result.stdout)
        self.assertIn("- current: ok", result.stdout)

    def test_missing_file_returns_non_zero(self) -> None:
        missing_path = ROOT / "tests" / "fixtures" / "support_metrics_contract" / "__missing_runtime_file__.jsonl"
        result = _run_tool(
            [
                "--baseline",
                str(missing_path),
                "--current",
                str(_fixture_path("recent_complete.jsonl")),
                "--check",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + "\n" + result.stderr
        self.assertIn("missing file", combined)

    def test_empty_file_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_file = Path(tmpdir) / "empty.jsonl"
            empty_file.write_text("", encoding="utf-8")
            result = _run_tool(
                [
                    "--baseline",
                    str(empty_file),
                    "--current",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--check",
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + "\n" + result.stderr
        self.assertIn("file is empty", combined)

    def test_invalid_json_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_file = Path(tmpdir) / "invalid.jsonl"
            invalid_file.write_text("{invalid json line\n", encoding="utf-8")
            result = _run_tool(
                [
                    "--baseline",
                    str(invalid_file),
                    "--current",
                    str(_fixture_path("recent_complete.jsonl")),
                    "--check",
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + "\n" + result.stderr
        self.assertIn("invalid JSON", combined)

    def test_partial_export_is_warning_but_not_error(self) -> None:
        result = _run_tool(
            [
                "--baseline",
                str(_fixture_path("partial_export.jsonl")),
                "--current",
                str(_fixture_path("recent_complete.jsonl")),
                "--check",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("- overall: warning", result.stdout)
        self.assertIn("partial support objectives coverage", result.stdout)

    def test_json_output_is_valid(self) -> None:
        result = _run_tool(
            [
                "--baseline",
                str(_fixture_path("recent_complete.jsonl")),
                "--current",
                str(_fixture_path("recent_complete.jsonl")),
                "--json",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload, dict)
        self.assertIn("overall", payload)
        self.assertIn("baseline", payload)
        self.assertIn("current", payload)
        self.assertIn("checked_files", payload)
        self.assertIn("issues_count", payload)
        self.assertIn("warnings_count", payload)

    def test_text_output_is_readable(self) -> None:
        result = _run_tool(
            [
                "--baseline",
                str(_fixture_path("recent_complete.jsonl")),
                "--current",
                str(_fixture_path("recent_complete.jsonl")),
                "--verbose",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics runtime files validation:", result.stdout)
        self.assertIn("- checked files: 2", result.stdout)
        self.assertIn("- baseline: ok", result.stdout)
        self.assertIn("- current: ok", result.stdout)
        self.assertIn("useful fields missing:", result.stdout)


if __name__ == "__main__":
    unittest.main()
