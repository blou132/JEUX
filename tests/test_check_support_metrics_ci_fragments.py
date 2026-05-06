from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.support_metrics_output_fragments import load_expected_fragments


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_support_metrics_ci_fragments.py"
FRAGMENTS_DIR = ROOT / "tests" / "fixtures" / "support_metrics_ci_outputs"
EXPECTED_FRAGMENT_FILES: tuple[str, ...] = (
    "manifest_summary_expected_fragments.txt",
    "manifest_report_expected_fragments.txt",
    "health_summary_expected_fragments.txt",
    "health_report_expected_fragments.txt",
    "contract_audit_summary_expected_fragments.txt",
    "contract_audit_report_expected_fragments.txt",
    "smoke_summary_expected_fragments.txt",
    "smoke_report_expected_fragments.txt",
    "runtime_skip_summary_expected_fragments.txt",
    "runtime_skip_report_expected_fragments.txt",
    "error_summary_expected_fragments.txt",
    "error_report_expected_fragments.txt",
    "local_simulation_summary_expected_fragments.txt",
    "local_simulation_report_expected_fragments.txt",
)


def _run_tool(extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    command: list[str] = [sys.executable, str(SCRIPT)]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class CheckSupportMetricsCIFragmentsToolTests(unittest.TestCase):
    def test_all_v190_fragment_files_exist(self) -> None:
        for file_name in EXPECTED_FRAGMENT_FILES:
            file_path = FRAGMENTS_DIR / file_name
            self.assertTrue(file_path.exists(), msg=f"Missing fragment fixture: {file_path}")

    def test_each_fragment_file_has_at_least_one_non_comment_fragment(self) -> None:
        for file_name in EXPECTED_FRAGMENT_FILES:
            file_path = FRAGMENTS_DIR / file_name
            fragments = load_expected_fragments(file_path)
            self.assertGreater(
                len(fragments),
                0,
                msg=f"Fragment fixture has no non-comment lines: {file_path}",
            )

    def test_list_outputs_categories_manifest_health_contract_audit_smoke_runtime_error_local(self) -> None:
        result = _run_tool(["--list"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Fragments list", result.stdout)
        self.assertIn("category=manifest", result.stdout)
        self.assertIn("category=health", result.stdout)
        self.assertIn("category=contract_audit", result.stdout)
        self.assertIn("category=smoke", result.stdout)
        self.assertIn("category=runtime", result.stdout)
        self.assertIn("category=error", result.stdout)
        self.assertIn("category=local", result.stdout)

    def test_validate_succeeds_with_current_fixtures(self) -> None:
        result = _run_tool(["--validate"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Validation status: valid", result.stdout)

    def test_validate_fails_cleanly_when_expected_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_fragments_dir = Path(tmpdir) / "fragments"
            temp_fragments_dir.mkdir(parents=True, exist_ok=True)

            result = _run_tool(
                [
                    "--validate",
                    "--print-missing",
                    "--fragments-dir",
                    str(temp_fragments_dir),
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing files", result.stdout)
            self.assertIn("smoke_summary_expected_fragments.txt", result.stdout)
            self.assertIn("Validation status: invalid", result.stdout)

    def test_validate_fails_cleanly_when_files_are_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_fragments_dir = Path(tmpdir) / "fragments"
            temp_fragments_dir.mkdir(parents=True, exist_ok=True)
            for file_name in EXPECTED_FRAGMENT_FILES:
                (temp_fragments_dir / file_name).write_text(
                    "# comment only\n\n   \n",
                    encoding="utf-8",
                )

            result = _run_tool(
                [
                    "--validate",
                    "--fragments-dir",
                    str(temp_fragments_dir),
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty fragment file", result.stdout)
            self.assertIn("Validation status: invalid", result.stdout)

    def test_validate_fails_when_health_fragment_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_fragments_dir = Path(tmpdir) / "fragments"
            temp_fragments_dir.mkdir(parents=True, exist_ok=True)
            for file_name in EXPECTED_FRAGMENT_FILES:
                if file_name == "health_report_expected_fragments.txt":
                    continue
                (temp_fragments_dir / file_name).write_text(
                    "required fragment\n",
                    encoding="utf-8",
                )

            result = _run_tool(
                [
                    "--validate",
                    "--print-missing",
                    "--fragments-dir",
                    str(temp_fragments_dir),
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("health_report_expected_fragments.txt", result.stdout)
            self.assertIn("Validation status: invalid", result.stdout)

    def test_validate_fails_when_contract_audit_fragment_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_fragments_dir = Path(tmpdir) / "fragments"
            temp_fragments_dir.mkdir(parents=True, exist_ok=True)
            for file_name in EXPECTED_FRAGMENT_FILES:
                if file_name == "contract_audit_report_expected_fragments.txt":
                    continue
                (temp_fragments_dir / file_name).write_text(
                    "required fragment\n",
                    encoding="utf-8",
                )

            result = _run_tool(
                [
                    "--validate",
                    "--print-missing",
                    "--fragments-dir",
                    str(temp_fragments_dir),
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract_audit_report_expected_fragments.txt", result.stdout)
            self.assertIn("Validation status: invalid", result.stdout)


if __name__ == "__main__":
    unittest.main()
