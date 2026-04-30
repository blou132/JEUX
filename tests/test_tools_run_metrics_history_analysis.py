from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "analyze_run_metrics_history.py"


def _write_jsonl(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


class RunMetricsHistoryAnalysisToolTests(unittest.TestCase):
    def test_valid_history_summary_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_001",
                        "run_status": "completed",
                        "objective_id": "support_gate",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 6,
                        "support_gate_run_success_rate": 1.0,
                        "support_gate_run_available_ratio": 0.60,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "exp_002",
                        "run_status": "failed",
                        "objective_id": "support_gate",
                        "objective_status": "failed",
                        "support_gate_run_attempts": 5,
                        "support_gate_run_success": 2,
                        "support_gate_run_success_rate": 0.40,
                        "support_gate_run_available_ratio": 0.30,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "exp_003",
                        "run_status": "running",
                        "objective_id": "observe_dominance",
                        "objective_status": "active",
                    }
                ),
            ]
            _write_jsonl(input_path, rows)

            result = subprocess.run(
                ["py", str(SCRIPT), "--input", str(input_path), "--format", "json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary = json.loads(result.stdout)

            self.assertEqual(summary["exports_read"], 3)
            self.assertEqual(summary["invalid_lines"], 0)
            self.assertEqual(summary["run_status_counts"]["completed"], 1)
            self.assertEqual(summary["run_status_counts"]["failed"], 1)
            self.assertEqual(summary["run_status_counts"]["running"], 1)
            self.assertEqual(summary["objective_counts"]["support_gate"], 2)
            self.assertEqual(summary["objective_counts"]["observe_dominance"], 1)

            support_gate = summary["support_gate"]
            self.assertEqual(support_gate["records"], 2)
            self.assertAlmostEqual(float(support_gate["avg_support_gate_run_attempts"]), 5.5, places=4)
            self.assertAlmostEqual(float(support_gate["avg_support_gate_run_success"]), 4.0, places=4)
            self.assertAlmostEqual(float(support_gate["avg_support_gate_run_success_rate"]), 0.7, places=4)
            self.assertAlmostEqual(float(support_gate["avg_support_gate_run_available_ratio"]), 0.45, places=4)
            self.assertEqual(support_gate["best_run"], "exp_001")
            self.assertEqual(support_gate["worst_run"], "exp_002")
            self.assertAlmostEqual(float(support_gate["objective_success_rate"]), 0.5, places=4)

    def test_invalid_lines_are_ignored_and_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps({"export_id": "exp_a", "run_status": "completed", "objective_id": "support_gate"}),
                "",
                "{ invalid json",
                "[]",
                json.dumps({"export_id": "exp_b"}),
            ]
            _write_jsonl(input_path, rows)

            result = subprocess.run(
                ["py", str(SCRIPT), "--input", str(input_path), "--format", "json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["invalid_lines"], 2)
            self.assertEqual(summary["exports_read"], 2)

    def test_missing_fields_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps({"export_id": "exp_010", "objective_id": "support_gate"}),
                json.dumps({"export_id": "exp_011", "objective_id": "support_gate", "objective_status": "active"}),
            ]
            _write_jsonl(input_path, rows)

            result = subprocess.run(
                ["py", str(SCRIPT), "--input", str(input_path), "--format", "json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            support_gate = summary["support_gate"]
            self.assertEqual(support_gate["records"], 2)
            self.assertIsNone(support_gate["avg_support_gate_run_attempts"])
            self.assertIsNone(support_gate["avg_support_gate_run_success"])
            self.assertIsNone(support_gate["avg_support_gate_run_success_rate"])
            self.assertIsNone(support_gate["avg_support_gate_run_available_ratio"])
            self.assertEqual(support_gate["best_run"], "n/a")
            self.assertEqual(support_gate["worst_run"], "n/a")
            self.assertIsNone(support_gate["objective_success_rate"])

    def test_objective_filter_and_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_101",
                        "run_status": "completed",
                        "objective_id": "support_gate",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.20,
                    }
                ),
                json.dumps({"export_id": "exp_102", "run_status": "failed", "objective_id": "observe_dominance"}),
                json.dumps(
                    {
                        "export_id": "exp_103",
                        "run_status": "completed",
                        "objective_id": "support_gate",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.70,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "exp_104",
                        "run_status": "failed",
                        "objective_id": "support_gate",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.30,
                    }
                ),
            ]
            _write_jsonl(input_path, rows)

            result = subprocess.run(
                [
                    "py",
                    str(SCRIPT),
                    "--input",
                    str(input_path),
                    "--objective",
                    "support_gate",
                    "--limit",
                    "2",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            summary = json.loads(result.stdout)

            self.assertEqual(summary["exports_read"], 2)
            self.assertEqual(summary["objective_filter"], "support_gate")
            self.assertEqual(summary["objective_counts"], {"support_gate": 2})
            self.assertEqual(summary["support_gate"]["records"], 2)


if __name__ == "__main__":
    unittest.main()
