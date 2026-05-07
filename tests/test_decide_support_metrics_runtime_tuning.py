from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "decide_support_metrics_runtime_tuning.py"
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


def _base_summary() -> dict[str, object]:
    return {
        "exports_read": 10,
        "support_gate": {
            "records": 10,
        },
        "support_systems_summary": {
            "data_state": "complete",
        },
        "support_metrics_quality": {
            "state": "valid",
            "warnings": [],
        },
        "support_metrics_regression": {
            "regression_state": "stable",
            "warning_count_delta": 0,
            "quality_state_changed": False,
            "support_gate_success_rate_delta": 0.0,
            "rally_champion_success_rate_delta": 0.0,
        },
        "support_metrics_final_decision": {
            "decision": "keep_candidate_for_more_testing",
        },
        "comparison": {
            "baseline_exports_read": 10,
            "candidate_exports_read": 10,
            "baseline_support_gate_records": 10,
            "candidate_support_gate_records": 10,
        },
    }


def _write_summary(path: Path, summary: dict[str, object]) -> None:
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


class DecideSupportMetricsRuntimeTuningToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--summary-json", result.stdout)
        self.assertIn("--baseline", result.stdout)
        self.assertIn("--current", result.stdout)
        self.assertIn("--min-runs", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--markdown-output", result.stdout)

    def test_runtime_absent_returns_collect_more_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = _base_summary()
            summary["exports_read"] = 0
            summary["support_systems_summary"] = {"data_state": "no_data"}
            summary["support_metrics_quality"] = {"state": "no_data", "warnings": ["no_support_metrics"]}
            summary["support_metrics_final_decision"] = {"decision": "no_runtime_data"}
            summary_path = Path(tmpdir) / "summary.json"
            _write_summary(summary_path, summary)

            result = _run_tool(["--summary-json", str(summary_path), "--json"])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "collect_more_runs")

    def test_quality_warning_returns_investigate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = _base_summary()
            summary["support_metrics_quality"] = {"state": "warning", "warnings": ["champion_success_rate_out_of_range"]}
            summary["support_metrics_regression"] = {
                "regression_state": "stable",
                "warning_count_delta": 0,
                "quality_state_changed": False,
                "support_gate_success_rate_delta": 0.0,
                "rally_champion_success_rate_delta": 0.0,
            }
            summary_path = Path(tmpdir) / "summary.json"
            _write_summary(summary_path, summary)

            result = _run_tool(["--summary-json", str(summary_path), "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "investigate_metrics")

    def test_regression_warning_returns_investigate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = _base_summary()
            summary["support_metrics_regression"] = {
                "regression_state": "warning",
                "warning_count_delta": 0,
                "quality_state_changed": False,
                "support_gate_success_rate_delta": -0.03,
                "rally_champion_success_rate_delta": 0.0,
            }
            summary_path = Path(tmpdir) / "summary.json"
            _write_summary(summary_path, summary)

            result = _run_tool(["--summary-json", str(summary_path), "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "investigate_metrics")

    def test_stable_with_sufficient_runs_returns_keep_tuning(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = _base_summary()
            summary["support_metrics_regression"] = {
                "regression_state": "stable",
                "warning_count_delta": 0,
                "quality_state_changed": False,
                "support_gate_success_rate_delta": 0.01,
                "rally_champion_success_rate_delta": 0.0,
            }
            summary_path = Path(tmpdir) / "summary.json"
            _write_summary(summary_path, summary)

            result = _run_tool(["--summary-json", str(summary_path), "--min-runs", "5", "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "keep_tuning")
            self.assertTrue(payload["minimum_runs_met"])

    def test_runs_insufficient_returns_collect_more_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = _base_summary()
            summary["comparison"] = {
                "baseline_exports_read": 2,
                "candidate_exports_read": 2,
                "baseline_support_gate_records": 2,
                "candidate_support_gate_records": 2,
            }
            summary_path = Path(tmpdir) / "summary.json"
            _write_summary(summary_path, summary)

            result = _run_tool(["--summary-json", str(summary_path), "--min-runs", "5", "--json"])
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision"], "collect_more_runs")
            self.assertFalse(payload["minimum_runs_met"])

    def test_json_output_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.json"
            _write_summary(summary_path, _base_summary())
            result = _run_tool(["--summary-json", str(summary_path), "--json"])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIsInstance(payload, dict)
            self.assertIn("decision", payload)
            self.assertIn("reasons", payload)
            self.assertIn("confidence", payload)
            self.assertIn("minimum_runs_met", payload)
            self.assertIn("gameplay_change_allowed", payload)
            self.assertFalse(payload["gameplay_change_allowed"])

    def test_markdown_output_contains_decision_and_reasons(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.json"
            markdown_path = Path(tmpdir) / "decision.md"
            _write_summary(summary_path, _base_summary())
            result = _run_tool(
                [
                    "--summary-json",
                    str(summary_path),
                    "--markdown-output",
                    str(markdown_path),
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(markdown_path.exists())
            content = markdown_path.read_text(encoding="utf-8")
            self.assertIn("- decision:", content)
            self.assertIn("- reasons:", content)

    def test_baseline_current_input_mode_works_without_godot(self) -> None:
        result = _run_tool(
            [
                "--baseline",
                str(_fixture_path("recent_complete.jsonl")),
                "--current",
                str(_fixture_path("recent_complete.jsonl")),
                "--min-runs",
                "5",
                "--json",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(payload["decision"], {"collect_more_runs", "keep_tuning", "investigate_metrics", "no_decision", "revert_tuning"})
        self.assertFalse(payload["gameplay_change_allowed"])


if __name__ == "__main__":
    unittest.main()
