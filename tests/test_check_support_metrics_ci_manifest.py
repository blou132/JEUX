from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.support_metrics_output_fragments import assert_expected_fragments_present


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_support_metrics_ci_manifest.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "tests.yml"
OUTPUT_CONTRACT_FIXTURES_DIR = ROOT / "tests" / "fixtures" / "support_metrics_ci_outputs"


VALID_MANIFEST: dict[str, list[str]] = {
    "tools": ["tools/example_tool.py"],
    "artifacts": ["support-metrics-smoke-report"],
    "fragment_categories": ["smoke"],
    "workflow_steps": ["Run unit tests"],
    "expected_invariants": ["CI/debug only"],
    "report_modes": ["smoke"],
}


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


def _write_valid_temp_repo(root_dir: Path) -> None:
    manifest_path = (
        root_dir
        / "tests"
        / "fixtures"
        / "support_metrics_ci_contract_manifest.json"
    )
    tool_path = root_dir / "tools" / "example_tool.py"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tool_path.parent.mkdir(parents=True, exist_ok=True)
    tool_path.write_text("# stub\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(VALID_MANIFEST, indent=2), encoding="utf-8")


class CheckSupportMetricsCIManifestToolTests(unittest.TestCase):
    def test_help_exposes_markdown_output_option(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--check", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--verbose", result.stdout)
        self.assertIn("--markdown-output", result.stdout)

    def test_manifest_check_nominal_is_ok(self) -> None:
        result = _run_tool(["--check"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Support metrics CI manifest:", result.stdout)
        self.assertIn("- overall: ok", result.stdout)

    def test_invalid_json_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_valid_temp_repo(temp_root)
            manifest_path = (
                temp_root
                / "tests"
                / "fixtures"
                / "support_metrics_ci_contract_manifest.json"
            )
            manifest_path.write_text("{invalid json", encoding="utf-8")

            result = _run_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("invalid JSON", result.stdout)

    def test_missing_required_key_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_valid_temp_repo(temp_root)
            manifest_path = (
                temp_root
                / "tests"
                / "fixtures"
                / "support_metrics_ci_contract_manifest.json"
            )
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            del parsed["tools"]
            manifest_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

            result = _run_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("manifest missing required key: tools", result.stdout)

    def test_empty_list_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_valid_temp_repo(temp_root)
            manifest_path = (
                temp_root
                / "tests"
                / "fixtures"
                / "support_metrics_ci_contract_manifest.json"
            )
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            parsed["artifacts"] = []
            manifest_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

            result = _run_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn("manifest key list is empty: artifacts", result.stdout)

    def test_duplicate_entry_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_valid_temp_repo(temp_root)
            manifest_path = (
                temp_root
                / "tests"
                / "fixtures"
                / "support_metrics_ci_contract_manifest.json"
            )
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            parsed["report_modes"] = ["smoke", "smoke"]
            manifest_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

            result = _run_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn(
                "manifest key list contains duplicate item: report_modes -> smoke",
                result.stdout,
            )

    def test_missing_tool_path_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir) / "repo"
            _write_valid_temp_repo(temp_root)
            manifest_path = (
                temp_root
                / "tests"
                / "fixtures"
                / "support_metrics_ci_contract_manifest.json"
            )
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            parsed["tools"] = ["tools/missing_tool.py"]
            manifest_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

            result = _run_tool(["--check", "--verbose", "--root", str(temp_root)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("- overall: error", result.stdout)
            self.assertIn(
                "manifest tool path is missing on disk: tools/missing_tool.py",
                result.stdout,
            )

    def test_json_output_is_valid(self) -> None:
        result = _run_tool(["--json"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        parsed = json.loads(result.stdout)
        self.assertIsInstance(parsed, dict)
        self.assertIn("overall", parsed)
        self.assertIn("manifest_path", parsed)
        self.assertIn("issues", parsed)
        self.assertIn("tools_count", parsed)
        self.assertIn("required_keys", parsed)

    def test_markdown_report_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_manifest.md"
            result = _run_tool(["--check", "--markdown-output", str(output_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Support metrics CI manifest", content)
            self.assertIn("- overall:", content)
            self.assertIn("not gameplay validation", content)

    def test_manifest_report_matches_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_manifest.md"
            result = _run_tool(["--check", "--markdown-output", str(report_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                report_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "manifest_report_expected_fragments.txt",
            )

    def test_manifest_summary_matches_output_snapshot_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "artifacts" / "support_metrics_ci_manifest.md"
            summary_path = Path(tmpdir) / "artifacts" / "github_step_summary.md"
            result = _run_tool(["--check", "--markdown-output", str(report_path)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(report_path.exists())

            report_text = report_path.read_text(encoding="utf-8")
            summary_path.write_text("## CI Summary\n\n" + report_text, encoding="utf-8")
            summary_text = summary_path.read_text(encoding="utf-8")
            assert_expected_fragments_present(
                self,
                summary_text,
                OUTPUT_CONTRACT_FIXTURES_DIR / "manifest_summary_expected_fragments.txt",
            )

    def test_workflow_contains_manifest_validation_step_and_keeps_core_steps(self) -> None:
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("Validate support metrics CI manifest", content)
        self.assertIn("py tools/check_support_metrics_ci_manifest.py --check --markdown-output", content)
        self.assertIn("support_metrics_ci_manifest.md", content)
        self.assertIn("support-metrics-ci-manifest", content)
        self.assertIn("GITHUB_STEP_SUMMARY", content)
        self.assertIn(
            "Get-Content \"$env:SUPPORT_METRICS_MANIFEST_REPORT_PATH\" | Add-Content -Path $env:GITHUB_STEP_SUMMARY",
            content,
        )
        self.assertIn("Upload support metrics CI manifest artifact", content)
        self.assertIn("if-no-files-found: error", content)
        self.assertIn("support-metrics-smoke-report", content)
        self.assertIn("support-metrics-report", content)
        self.assertIn("support-metrics-ci-health", content)
        self.assertIn("support-metrics-ci-contract-audit", content)
        self.assertIn("Validate support metrics CI fragments", content)
        self.assertIn("Validate support metrics CI health", content)
        self.assertIn("Validate support metrics CI contract audit", content)
        self.assertIn("Smoke test support metrics CI summary", content)
        self.assertIn("Optional runtime support metrics CI check", content)
        self.assertNotIn("--fail-on-regression", content)


if __name__ == "__main__":
    unittest.main()
