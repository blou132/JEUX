from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "analyze_run_metrics_history.py"


def _write_jsonl(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _run_summary_json(input_path: Path, extra_args: list[str] | None = None) -> dict:
    command = [sys.executable, str(SCRIPT), "--input", str(input_path), "--format", "json"]
    if extra_args:
        command.extend(extra_args)
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return json.loads(result.stdout)


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _run_comparison_summary_json(baseline_rows: list[str], candidate_rows: list[str]) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        baseline_path = Path(tmpdir) / "before.jsonl"
        candidate_path = Path(tmpdir) / "after.jsonl"
        _write_jsonl(baseline_path, baseline_rows)
        _write_jsonl(candidate_path, candidate_rows)
        return _run_summary_json(
            baseline_path,
            ["--compare-input", str(candidate_path)],
        )


def _build_support_gate_rows(
    prefix: str,
    count: int,
    success_rate: float = 0.60,
    available_ratio: float = 0.50,
    run_status: str = "completed",
    objective_status: str = "completed",
) -> list[str]:
    rows: list[str] = []
    run_success = max(0, min(6, int(round(6 * success_rate))))
    for index in range(count):
        rows.append(
            json.dumps(
                {
                    "export_id": f"{prefix}_{index + 1}",
                    "objective_id": "support_gate",
                    "run_status": run_status,
                    "objective_status": objective_status,
                    "support_gate_run_attempts": 6,
                    "support_gate_run_success": run_success,
                    "support_gate_run_success_rate": success_rate,
                    "support_gate_run_available_ratio": available_ratio,
                }
            )
        )
    return rows


def _run_summary_from_rows(rows: list[str]) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "run_metrics_history.jsonl"
        _write_jsonl(input_path, rows)
        return _run_summary_json(input_path)


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

            summary = _run_summary_json(input_path)

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
            champion_support = summary["champion_support"]
            self.assertEqual(champion_support["records"], 0)
            self.assertIsNone(champion_support["avg_champion_support_run_attempts"])
            self.assertIsNone(champion_support["avg_champion_support_run_success"])
            self.assertIsNone(champion_support["avg_champion_support_run_success_rate"])
            self.assertEqual(champion_support["best_run"], "n/a")
            self.assertEqual(champion_support["worst_run"], "n/a")
            self.assertIsNone(champion_support["objective_success_rate"])
            self.assertEqual(champion_support["latest_champion_support_tuning_label"], "")
            support_systems_summary = summary["support_systems_summary"]
            self.assertEqual(support_systems_summary["data_state"], "partial")
            self.assertEqual(support_systems_summary["interpretation"], "partial_data")
            support_metrics_quality = summary["support_metrics_quality"]
            self.assertEqual(support_metrics_quality["state"], "incomplete")
            self.assertIn("champion_support_missing", support_metrics_quality["warnings"])
            self.assertIn("final_decision", summary)

    def test_champion_support_metrics_are_aggregated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "champ_001",
                        "run_status": "completed",
                        "objective_id": "rally_champion",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 4,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.75,
                        "champion_support_tuning_label": "Champion support: run attempts=4 success=3 rate=75%",
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_002",
                        "run_status": "failed",
                        "objective_id": "rally_champion",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 2,
                        "champion_support_run_success_rate": 0.40,
                        "champion_support_tuning_label": "Champion support: run attempts=5 success=2 rate=40%",
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_001",
                        "run_status": "completed",
                        "objective_id": "support_gate",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 6,
                        "support_gate_run_success_rate": 1.0,
                        "support_gate_run_available_ratio": 0.60,
                    }
                ),
            ]
            _write_jsonl(input_path, rows)

            summary = _run_summary_json(input_path)
            champion_support = summary["champion_support"]
            self.assertEqual(champion_support["records"], 2)
            self.assertAlmostEqual(float(champion_support["avg_champion_support_run_attempts"]), 4.5, places=4)
            self.assertAlmostEqual(float(champion_support["avg_champion_support_run_success"]), 2.5, places=4)
            self.assertAlmostEqual(float(champion_support["avg_champion_support_run_success_rate"]), 0.575, places=4)
            self.assertEqual(champion_support["best_run"], "champ_001")
            self.assertEqual(champion_support["worst_run"], "champ_002")
            self.assertAlmostEqual(float(champion_support["objective_success_rate"]), 0.5, places=4)
            self.assertEqual(
                champion_support["latest_champion_support_tuning_label"],
                "Champion support: run attempts=5 success=2 rate=40%",
            )
            self.assertEqual(summary["support_gate"]["records"], 1)

    def test_champion_support_recent_export_fields_feed_diagnostic(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_recent_1",
                        "run_status": "completed",
                        "objective_id": "rally_champion",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 4,
                        "champion_support_run_success": 1,
                        "champion_support_run_success_rate": 0.25,
                        "champion_support_attempts_total": 4,
                        "champion_support_success_total": 1,
                        "champion_support_unavailable_total": 1,
                        "champion_support_cooldown_blocked_total": 2,
                        "champion_support_completed_total": 1,
                        "champion_support_failed_total": 0,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_recent_2",
                        "run_status": "failed",
                        "objective_id": "rally_champion",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 6,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.50,
                        "champion_support_attempts_total": 6,
                        "champion_support_success_total": 3,
                        "champion_support_unavailable_total": 2,
                        "champion_support_cooldown_blocked_total": 1,
                        "champion_support_completed_total": 1,
                        "champion_support_failed_total": 1,
                    }
                ),
            ]
        )
        champion_support = summary["champion_support"]
        self.assertAlmostEqual(float(champion_support["avg_champion_support_attempts_total"]), 5.0, places=4)
        self.assertAlmostEqual(float(champion_support["avg_champion_support_success_total"]), 2.0, places=4)
        self.assertAlmostEqual(float(champion_support["avg_champion_support_unavailable_total"]), 1.5, places=4)
        self.assertAlmostEqual(float(champion_support["avg_champion_support_cooldown_blocked_total"]), 1.5, places=4)
        self.assertAlmostEqual(float(champion_support["avg_champion_support_completed_total"]), 1.0, places=4)
        self.assertAlmostEqual(float(champion_support["avg_champion_support_failed_total"]), 0.5, places=4)
        diagnostic = champion_support["diagnostic"]
        self.assertAlmostEqual(float(diagnostic["attempts_avg"]), 5.0, places=4)
        self.assertAlmostEqual(float(diagnostic["success_rate_avg"]), 0.375, places=4)
        self.assertEqual(diagnostic["cooldown_pressure"], "medium")
        self.assertEqual(diagnostic["unavailable_pressure"], "medium")
        self.assertEqual(diagnostic["objective_completion"], "1/2")
        self.assertIn("low success rate", str(diagnostic["interpretation"]))

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

            summary = _run_summary_json(input_path)
            self.assertEqual(summary["invalid_lines"], 2)
            self.assertEqual(summary["exports_read"], 2)
            recommendations = summary["recommendations"]
            self.assertTrue(any("ignored" in recommendation.lower() for recommendation in recommendations))

    def test_missing_fields_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps({"export_id": "exp_010", "objective_id": "support_gate"}),
                json.dumps({"export_id": "exp_011", "objective_id": "support_gate", "objective_status": "active"}),
            ]
            _write_jsonl(input_path, rows)

            summary = _run_summary_json(input_path)
            support_gate = summary["support_gate"]
            self.assertEqual(support_gate["records"], 2)
            self.assertIsNone(support_gate["avg_support_gate_run_attempts"])
            self.assertIsNone(support_gate["avg_support_gate_run_success"])
            self.assertIsNone(support_gate["avg_support_gate_run_success_rate"])
            self.assertIsNone(support_gate["avg_support_gate_run_available_ratio"])
            self.assertEqual(support_gate["best_run"], "n/a")
            self.assertEqual(support_gate["worst_run"], "n/a")
            self.assertIsNone(support_gate["objective_success_rate"])
            champion_support = summary["champion_support"]
            self.assertEqual(champion_support["records"], 0)

    def test_missing_champion_fields_do_not_crash_for_old_rally_exports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "old_rally_1",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                    }
                ),
                json.dumps(
                    {
                        "export_id": "old_rally_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                    }
                ),
            ]
            _write_jsonl(input_path, rows)

            summary = _run_summary_json(input_path)
            champion_support = summary["champion_support"]
            self.assertEqual(champion_support["records"], 2)
            self.assertIsNone(champion_support["avg_champion_support_run_attempts"])
            self.assertIsNone(champion_support["avg_champion_support_run_success"])
            self.assertIsNone(champion_support["avg_champion_support_run_success_rate"])
            self.assertEqual(champion_support["best_run"], "n/a")
            self.assertEqual(champion_support["worst_run"], "n/a")
            self.assertAlmostEqual(float(champion_support["objective_success_rate"]), 0.5, places=4)
            self.assertEqual(champion_support["latest_champion_support_tuning_label"], "")
            diagnostic = champion_support["diagnostic"]
            self.assertIsNone(diagnostic["attempts_avg"])
            self.assertIsNone(diagnostic["success_rate_avg"])
            self.assertEqual(diagnostic["cooldown_pressure"], "n/a")
            self.assertEqual(diagnostic["unavailable_pressure"], "n/a")
            self.assertEqual(diagnostic["objective_completion"], "1/2")
            self.assertEqual(diagnostic["interpretation"], "n/a")
            multi_run = champion_support["multi_run_comparison"]
            self.assertIsNone(multi_run["avg_attempts"])
            self.assertIsNone(multi_run["avg_success"])
            self.assertIsNone(multi_run["avg_success_rate"])
            self.assertIsNone(multi_run["avg_cooldown"])
            self.assertIsNone(multi_run["avg_unavailable"])
            self.assertEqual(multi_run["objective_completed"], 1)
            self.assertEqual(multi_run["objective_failed"], 1)
            self.assertEqual(multi_run["diagnostic_stability"], "n/a")
            self.assertEqual(multi_run["global_interpretation"], "no_data")
            self.assertIn("support_gate", summary)

    def test_champion_support_diagnostic_flags_low_success_rate(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_low_success_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 1,
                        "champion_support_run_success_rate": 0.20,
                        "champion_support_attempts_total": 5,
                        "champion_support_success_total": 1,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                        "champion_support_completed_total": 0,
                        "champion_support_failed_total": 1,
                    }
                )
            ]
        )
        diagnostic = summary["champion_support"]["diagnostic"]
        self.assertIn("low success rate", str(diagnostic["interpretation"]))
        self.assertIn("support_gate", summary)

    def test_champion_support_diagnostic_flags_high_cooldown_pressure(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_cooldown_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_success_total": 3,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 4,
                        "champion_support_completed_total": 0,
                        "champion_support_failed_total": 1,
                    }
                )
            ]
        )
        diagnostic = summary["champion_support"]["diagnostic"]
        self.assertEqual(diagnostic["cooldown_pressure"], "high")
        self.assertIn("high cooldown pressure", str(diagnostic["interpretation"]))

    def test_champion_support_diagnostic_flags_high_unavailable_pressure(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_unavailable_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_success_total": 3,
                        "champion_support_unavailable_total": 4,
                        "champion_support_cooldown_blocked_total": 0,
                        "champion_support_completed_total": 0,
                        "champion_support_failed_total": 1,
                    }
                )
            ]
        )
        diagnostic = summary["champion_support"]["diagnostic"]
        self.assertEqual(diagnostic["unavailable_pressure"], "high")
        self.assertIn("high unavailable pressure", str(diagnostic["interpretation"]))

    def test_champion_multi_run_comparison_stable_successful(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_stable_1",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_stable_2",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 4,
                        "champion_support_run_success_rate": 0.70,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_keep_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.60,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
            ]
        )
        multi_run = summary["champion_support"]["multi_run_comparison"]
        self.assertAlmostEqual(float(multi_run["avg_attempts"]), 5.0, places=4)
        self.assertAlmostEqual(float(multi_run["avg_success"]), 3.5, places=4)
        self.assertAlmostEqual(float(multi_run["avg_success_rate"]), 0.65, places=4)
        self.assertAlmostEqual(float(multi_run["avg_cooldown"]), 1.0, places=4)
        self.assertAlmostEqual(float(multi_run["avg_unavailable"]), 0.0, places=4)
        self.assertEqual(multi_run["objective_completed"], 2)
        self.assertEqual(multi_run["objective_failed"], 0)
        self.assertEqual(multi_run["diagnostic_stability"], "stable")
        self.assertEqual(multi_run["global_interpretation"], "stable_successful")
        self.assertIn("support_gate", summary)

    def test_champion_multi_run_comparison_unstable_success(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_unstable_1",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 4,
                        "champion_support_run_success_rate": 0.80,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_unstable_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 1,
                        "champion_support_run_success_rate": 0.20,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_keep_2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.60,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
            ]
        )
        multi_run = summary["champion_support"]["multi_run_comparison"]
        self.assertEqual(multi_run["diagnostic_stability"], "unstable")
        self.assertEqual(multi_run["global_interpretation"], "unstable_success")
        self.assertIn("support_gate", summary)

    def test_champion_multi_run_comparison_cooldown_bottleneck(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_cd_multi_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 4,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_cd_multi_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 2,
                        "champion_support_run_success_rate": 0.40,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 4,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_keep_3",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.40,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
            ]
        )
        multi_run = summary["champion_support"]["multi_run_comparison"]
        self.assertEqual(multi_run["global_interpretation"], "cooldown_bottleneck")
        self.assertIn("support_gate", summary)

    def test_champion_multi_run_comparison_unavailable_bottleneck(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_un_multi_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 4,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_un_multi_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 2,
                        "champion_support_run_success_rate": 0.40,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 4,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_keep_4",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.40,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
            ]
        )
        multi_run = summary["champion_support"]["multi_run_comparison"]
        self.assertEqual(multi_run["global_interpretation"], "unavailable_bottleneck")
        self.assertIn("support_gate", summary)

    def test_champion_multi_run_comparison_low_attempts(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "champ_low_attempts_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 1,
                        "champion_support_run_success": 0,
                        "champion_support_run_success_rate": 0.0,
                        "champion_support_attempts_total": 1,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_low_attempts_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 1,
                        "champion_support_run_success": 0,
                        "champion_support_run_success_rate": 0.0,
                        "champion_support_attempts_total": 1,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
            ]
        )
        multi_run = summary["champion_support"]["multi_run_comparison"]
        self.assertEqual(multi_run["global_interpretation"], "low_attempts")

    def test_support_systems_summary_complete_and_both_stable(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "gate_stable_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 4,
                        "support_gate_run_success_rate": 0.60,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_stable_2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 4,
                        "support_gate_run_success_rate": 0.62,
                        "support_gate_run_available_ratio": 0.52,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_stable_1",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_stable_2",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.62,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
            ]
        )
        support_summary = summary["support_systems_summary"]
        self.assertEqual(support_summary["data_state"], "complete")
        self.assertEqual(support_summary["interpretation"], "both_stable")
        self.assertEqual(support_summary["support_gate_main_bottleneck"], "none")
        self.assertEqual(support_summary["rally_champion_global_interpretation"], "stable_successful")

    def test_support_systems_summary_support_gate_present_champion_absent(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "gate_only_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 4,
                        "support_gate_run_success_rate": 0.60,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ]
        )
        support_summary = summary["support_systems_summary"]
        self.assertEqual(support_summary["data_state"], "partial")
        self.assertEqual(support_summary["interpretation"], "partial_data")
        self.assertIn("support_gate", summary)

    def test_support_systems_summary_champion_present_support_gate_partial(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "gate_partial_1",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_present_1",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 1,
                    }
                ),
            ]
        )
        support_summary = summary["support_systems_summary"]
        self.assertEqual(support_summary["data_state"], "partial")
        self.assertEqual(support_summary["interpretation"], "partial_data")
        self.assertIn("support_gate", summary)

    def test_support_systems_summary_old_exports_without_champion_metrics(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "old_1",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                    }
                ),
                json.dumps(
                    {
                        "export_id": "old_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                    }
                ),
            ]
        )
        support_summary = summary["support_systems_summary"]
        self.assertEqual(support_summary["data_state"], "no_data")
        self.assertEqual(support_summary["interpretation"], "no_data")
        self.assertIn("support_gate", summary)

    def test_support_systems_summary_both_limited(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "gate_limited_1",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 2,
                        "support_gate_run_success_rate": 0.30,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "gate_limited_2",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 2,
                        "support_gate_run_success_rate": 0.32,
                        "support_gate_run_available_ratio": 0.52,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_limited_1",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 4,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "champ_limited_2",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 2,
                        "champion_support_run_success_rate": 0.40,
                        "champion_support_attempts_total": 5,
                        "champion_support_unavailable_total": 4,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
            ]
        )
        support_summary = summary["support_systems_summary"]
        self.assertEqual(support_summary["data_state"], "complete")
        self.assertEqual(support_summary["interpretation"], "both_limited")
        self.assertEqual(support_summary["support_gate_main_bottleneck"], "success_rate")
        self.assertEqual(support_summary["rally_champion_global_interpretation"], "unavailable_bottleneck")

    def test_support_metrics_quality_valid(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_valid_gate_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 4,
                        "support_gate_run_success_rate": 0.66,
                        "support_gate_run_available_ratio": 0.50,
                        "support_gate_run_cooldown_blocked": 1,
                        "support_gate_run_unavailable": 0,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "quality_valid_champ_1",
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
                    }
                ),
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "valid")
        self.assertEqual(quality["warnings"], [])

    def test_support_metrics_quality_success_greater_than_attempts(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_bad_success",
                        "objective_id": "rally_champion",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "champion_support_run_attempts": 2,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.80,
                        "champion_support_attempts_total": 2,
                        "champion_support_success_total": 3,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                )
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "warning")
        self.assertIn("champion_success_greater_than_attempts", quality["warnings"])

    def test_support_metrics_quality_success_rate_out_of_range(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_bad_rate",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 4,
                        "support_gate_run_success": 3,
                        "support_gate_run_success_rate": 1.20,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "quality_bad_rate_champ",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "champion_support_run_attempts": 5,
                        "champion_support_run_success": 3,
                        "champion_support_run_success_rate": 0.60,
                        "champion_support_attempts_total": 5,
                        "champion_support_success_total": 3,
                        "champion_support_unavailable_total": 0,
                        "champion_support_cooldown_blocked_total": 0,
                    }
                ),
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "warning")
        self.assertIn("support_gate_success_rate_out_of_range", quality["warnings"])

    def test_support_metrics_quality_champion_absent_is_incomplete(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_gate_only",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 4,
                        "support_gate_run_success": 3,
                        "support_gate_run_success_rate": 0.75,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "incomplete")
        self.assertIn("champion_support_missing", quality["warnings"])

    def test_support_metrics_quality_support_gate_absent_is_incomplete(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_champ_only",
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
                    }
                )
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "incomplete")
        self.assertIn("support_gate_missing", quality["warnings"])

    def test_support_metrics_quality_partial_legacy_export(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_partial_gate",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 4,
                        "support_gate_run_success": 2,
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "quality_partial_legacy",
                        "objective_id": "rally_champion",
                        "run_status": "completed",
                        "objective_status": "completed",
                    }
                ),
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "incomplete")
        self.assertIn("partial_legacy_export", quality["warnings"])

    def test_support_metrics_quality_no_support_metrics(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "quality_none",
                        "objective_id": "observe_dominance",
                        "run_status": "running",
                        "objective_status": "active",
                    }
                )
            ]
        )
        quality = summary["support_metrics_quality"]
        self.assertEqual(quality["state"], "no_data")
        self.assertIn("no_support_metrics", quality["warnings"])

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

            summary = _run_summary_json(
                input_path,
                ["--objective", "support_gate", "--limit", "2"],
            )

            self.assertEqual(summary["exports_read"], 2)
            self.assertEqual(summary["objective_filter"], "support_gate")
            self.assertEqual(summary["objective_counts"], {"support_gate": 2})
            self.assertEqual(summary["support_gate"]["records"], 2)

    def test_recommendations_no_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps({"export_id": "exp_n1", "objective_id": "observe_dominance", "run_status": "running"}),
            ]
            _write_jsonl(input_path, rows)
            summary = _run_summary_json(input_path)
            self.assertIn("Not enough support_gate data.", summary["recommendations"])
            self.assertEqual(summary["final_decision"], "Collect support_gate runs first.")

    def test_recommendations_low_available_ratio(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_a1",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.60,
                        "support_gate_run_available_ratio": 0.10,
                    }
                )
            ]
            _write_jsonl(input_path, rows)
            summary = _run_summary_json(input_path)
            recommendations = summary["recommendations"]
            self.assertTrue(any("availability looks low" in recommendation.lower() for recommendation in recommendations))

    def test_recommendations_low_success_rate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_b1",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.30,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ]
            _write_jsonl(input_path, rows)
            summary = _run_summary_json(input_path)
            recommendations = summary["recommendations"]
            self.assertTrue(any("success rate is low" in recommendation.lower() for recommendation in recommendations))

    def test_recommendations_objective_too_easy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_c1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.90,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "exp_c2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.95,
                        "support_gate_run_available_ratio": 0.60,
                    }
                ),
            ]
            _write_jsonl(input_path, rows)
            summary = _run_summary_json(input_path)
            recommendations = summary["recommendations"]
            self.assertTrue(any("too easy" in recommendation.lower() for recommendation in recommendations))

    def test_recommendations_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_d1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.60,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "exp_d2",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.55,
                        "support_gate_run_available_ratio": 0.45,
                    }
                ),
            ]
            _write_jsonl(input_path, rows)
            summary = _run_summary_json(input_path)
            self.assertIn("Support gate tuning looks stable.", summary["recommendations"])

    def test_final_decision_stable_no_comparison(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "stable_decision_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.45,
                        "support_gate_run_available_ratio": 0.55,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stable_decision_2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stable_decision_3",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.55,
                        "support_gate_run_available_ratio": 0.45,
                    }
                ),
            ]
        )
        self.assertEqual(summary["final_decision"], "Current support_gate tuning looks acceptable.")

    def test_support_gate_stability_unknown(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "stability_unknown_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ]
        )
        support_gate = summary["support_gate"]
        self.assertEqual(support_gate["support_gate_stability_label"], "unknown")
        self.assertIsNone(support_gate["stddev_support_gate_run_success_rate"])
        self.assertIsNone(support_gate["stddev_support_gate_run_available_ratio"])

    def test_support_gate_stability_stable(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "stability_stable_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.45,
                        "support_gate_run_available_ratio": 0.55,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stability_stable_2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stability_stable_3",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.55,
                        "support_gate_run_available_ratio": 0.45,
                    }
                ),
            ]
        )
        self.assertEqual(summary["support_gate"]["support_gate_stability_label"], "stable")

    def test_support_gate_stability_variable(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "stability_variable_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.20,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stability_variable_2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stability_variable_3",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.80,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
            ]
        )
        self.assertEqual(summary["support_gate"]["support_gate_stability_label"], "variable")

    def test_support_gate_stability_unstable_and_recommendation(self) -> None:
        summary = _run_summary_from_rows(
            [
                json.dumps(
                    {
                        "export_id": "stability_unstable_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.00,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stability_unstable_2",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
                json.dumps(
                    {
                        "export_id": "stability_unstable_3",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 1.00,
                        "support_gate_run_available_ratio": 0.50,
                    }
                ),
            ]
        )
        self.assertEqual(summary["support_gate"]["support_gate_stability_label"], "unstable")
        self.assertIn(
            "Support gate results vary a lot: run more tests before changing tuning.",
            summary["recommendations"],
        )

    def test_text_output_includes_recommendations_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_t1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.65,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ]
            _write_jsonl(input_path, rows)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(input_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("Recommendations:", result.stdout)
            self.assertIn("Support gate tuning looks stable.", result.stdout)
            self.assertIn("Support gate stability:", result.stdout)
            self.assertIn("Champion support diagnostic:", result.stdout)
            self.assertIn("Champion support multi-run comparison:", result.stdout)
            self.assertIn("Support systems summary:", result.stdout)
            self.assertIn("Support metrics quality:", result.stdout)
            self.assertIn("- state:", result.stdout)
            self.assertIn("- warnings:", result.stdout)
            self.assertIn("- support_gate:", result.stdout)
            self.assertIn("- rally_champion:", result.stdout)
            self.assertIn("Final decision:", result.stdout)

    def test_markdown_output_contains_expected_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_m1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 4,
                        "support_gate_run_success_rate": 0.67,
                        "support_gate_run_available_ratio": 0.52,
                    }
                )
            ]
            _write_jsonl(input_path, rows)

            result = _run_cli(["--input", str(input_path), "--format", "markdown"])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("# Run Metrics History Analysis", result.stdout)
            self.assertIn("## Support gate", result.stdout)
            self.assertIn("## Champion support", result.stdout)
            self.assertIn("### Champion support diagnostic", result.stdout)
            self.assertIn("### Champion support multi-run comparison", result.stdout)
            self.assertIn("### Support systems summary", result.stdout)
            self.assertIn("### Support metrics quality", result.stdout)
            self.assertIn("## Recommendations", result.stdout)
            self.assertIn("| support gate stability |", result.stdout)
            self.assertIn("## Final decision", result.stdout)

    def test_output_option_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "run_metrics_history.jsonl"
            output_path = Path(tmpdir) / "reports" / "run_metrics_report.md"
            rows = [
                json.dumps(
                    {
                        "export_id": "exp_o1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.80,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ]
            _write_jsonl(input_path, rows)

            result = _run_cli(
                [
                    "--input",
                    str(input_path),
                    "--format",
                    "md",
                    "--output",
                    str(output_path),
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Run Metrics History Analysis", content)

    def test_comparison_json_contains_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "before.jsonl"
            candidate_path = Path(tmpdir) / "after.jsonl"

            baseline_rows = [
                json.dumps(
                    {
                        "export_id": "before_1",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_attempts": 6,
                        "support_gate_run_success": 3,
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.60,
                    }
                )
            ]
            candidate_rows = [
                json.dumps(
                    {
                        "export_id": "after_1",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_attempts": 5,
                        "support_gate_run_success": 3,
                        "support_gate_run_success_rate": 0.70,
                        "support_gate_run_available_ratio": 0.40,
                    }
                )
            ]
            _write_jsonl(baseline_path, baseline_rows)
            _write_jsonl(candidate_path, candidate_rows)

            summary = _run_summary_json(
                baseline_path,
                ["--compare-input", str(candidate_path)],
            )
            comparison = summary["comparison"]
            support_gate_comparison = comparison["support_gate"]
            delta = support_gate_comparison["delta"]

            self.assertIn("confidence", comparison)
            self.assertAlmostEqual(float(delta["avg_support_gate_run_success_rate"]), 0.20, places=4)
            self.assertAlmostEqual(float(delta["avg_support_gate_run_available_ratio"]), -0.20, places=4)
            self.assertAlmostEqual(float(delta["avg_support_gate_run_attempts"]), -1.0, places=4)
            self.assertAlmostEqual(float(delta["avg_support_gate_run_success"]), 0.0, places=4)
            self.assertAlmostEqual(float(delta["objective_success_rate"]), -1.0, places=4)

    def test_comparison_confidence_low(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=_build_support_gate_rows("base_low", 2),
            candidate_rows=_build_support_gate_rows("cand_low", 5),
        )
        self.assertEqual(summary["comparison"]["confidence"], "low")

    def test_final_decision_comparison_low_confidence(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=_build_support_gate_rows("base_low_decision", 2, success_rate=0.50),
            candidate_rows=_build_support_gate_rows("cand_low_decision", 2, success_rate=0.80),
        )
        self.assertEqual(summary["comparison"]["confidence"], "low")
        self.assertEqual(summary["final_decision"], "Collect more runs before deciding.")

    def test_comparison_confidence_medium(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=_build_support_gate_rows("base_med", 3),
            candidate_rows=_build_support_gate_rows("cand_med", 9),
        )
        self.assertEqual(summary["comparison"]["confidence"], "medium")

    def test_comparison_confidence_high(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=_build_support_gate_rows("base_high", 10),
            candidate_rows=_build_support_gate_rows("cand_high", 12),
        )
        self.assertEqual(summary["comparison"]["confidence"], "high")

    def test_final_decision_comparison_better_with_medium_confidence(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=_build_support_gate_rows("base_better_decision", 3, success_rate=0.50, available_ratio=0.50),
            candidate_rows=_build_support_gate_rows("cand_better_decision", 3, success_rate=0.70, available_ratio=0.48),
        )
        self.assertEqual(summary["comparison"]["confidence"], "medium")
        self.assertEqual(summary["comparison"]["recommendation"], "Candidate looks better for support_gate.")
        self.assertEqual(summary["final_decision"], "Candidate tuning can be kept for further testing.")

    def test_final_decision_comparison_worse(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=_build_support_gate_rows("base_worse_decision", 3, success_rate=0.70, available_ratio=0.50, run_status="completed", objective_status="completed"),
            candidate_rows=_build_support_gate_rows("cand_worse_decision", 3, success_rate=0.40, available_ratio=0.45, run_status="failed", objective_status="failed"),
        )
        self.assertEqual(summary["comparison"]["recommendation"], "Candidate looks worse for support_gate.")
        self.assertEqual(summary["final_decision"], "Reject candidate tuning or revert.")

    def test_comparison_markdown_contains_comparison_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "before.jsonl"
            candidate_path = Path(tmpdir) / "after.jsonl"
            _write_jsonl(
                baseline_path,
                [
                    json.dumps(
                        {
                            "export_id": "before_md_1",
                            "objective_id": "support_gate",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "support_gate_run_success_rate": 0.55,
                            "support_gate_run_available_ratio": 0.50,
                        }
                    )
                ],
            )
            _write_jsonl(
                candidate_path,
                [
                    json.dumps(
                        {
                            "export_id": "after_md_1",
                            "objective_id": "support_gate",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "support_gate_run_success_rate": 0.65,
                            "support_gate_run_available_ratio": 0.45,
                        }
                    )
                ],
            )

            result = _run_cli(
                [
                    "--input",
                    str(baseline_path),
                    "--compare-input",
                    str(candidate_path),
                    "--format",
                    "markdown",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("## Comparison", result.stdout)
            self.assertIn("| Metric | Baseline | Candidate | Delta | Change |", result.stdout)

    def test_compare_input_missing_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "before.jsonl"
            missing_candidate_path = Path(tmpdir) / "missing_after.jsonl"
            _write_jsonl(
                baseline_path,
                [json.dumps({"export_id": "before_missing", "objective_id": "support_gate"})],
            )

            result = _run_cli(
                [
                    "--input",
                    str(baseline_path),
                    "--compare-input",
                    str(missing_candidate_path),
                    "--format",
                    "json",
                ]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("ERROR: compare input file not found", result.stdout)

    def test_comparison_recommendation_better(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=[
                json.dumps(
                    {
                        "export_id": "before_better",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ],
            candidate_rows=[
                json.dumps(
                    {
                        "export_id": "after_better",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.70,
                        "support_gate_run_available_ratio": 0.48,
                    }
                )
            ],
        )
        self.assertEqual(
            summary["comparison"]["recommendation"],
            "Candidate looks better for support_gate.",
        )

    def test_comparison_recommendation_worse(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=[
                json.dumps(
                    {
                        "export_id": "before_worse",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.70,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ],
            candidate_rows=[
                json.dumps(
                    {
                        "export_id": "after_worse",
                        "objective_id": "support_gate",
                        "run_status": "failed",
                        "objective_status": "failed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.45,
                    }
                )
            ],
        )
        self.assertEqual(
            summary["comparison"]["recommendation"],
            "Candidate looks worse for support_gate.",
        )

    def test_comparison_recommendation_mixed(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=[
                json.dumps(
                    {
                        "export_id": "before_mixed",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.50,
                        "support_gate_run_available_ratio": 0.60,
                    }
                )
            ],
            candidate_rows=[
                json.dumps(
                    {
                        "export_id": "after_mixed",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.70,
                        "support_gate_run_available_ratio": 0.45,
                    }
                )
            ],
        )
        self.assertEqual(
            summary["comparison"]["recommendation"],
            "Mixed result: success improved but availability got worse.",
        )

    def test_comparison_recommendation_insufficient_data(self) -> None:
        summary = _run_comparison_summary_json(
            baseline_rows=[
                json.dumps(
                    {
                        "export_id": "before_insufficient",
                        "objective_id": "observe_dominance",
                        "run_status": "running",
                        "objective_status": "active",
                    }
                )
            ],
            candidate_rows=[
                json.dumps(
                    {
                        "export_id": "after_insufficient",
                        "objective_id": "support_gate",
                        "run_status": "completed",
                        "objective_status": "completed",
                        "support_gate_run_success_rate": 0.65,
                        "support_gate_run_available_ratio": 0.50,
                    }
                )
            ],
        )
        self.assertEqual(
            summary["comparison"]["recommendation"],
            "Insufficient support_gate data for comparison.",
        )

    def test_comparison_markdown_contains_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "before_rec.jsonl"
            candidate_path = Path(tmpdir) / "after_rec.jsonl"
            _write_jsonl(
                baseline_path,
                [
                    json.dumps(
                        {
                            "export_id": "before_rec",
                            "objective_id": "support_gate",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "support_gate_run_success_rate": 0.50,
                            "support_gate_run_available_ratio": 0.50,
                        }
                    )
                ],
            )
            _write_jsonl(
                candidate_path,
                [
                    json.dumps(
                        {
                            "export_id": "after_rec",
                            "objective_id": "support_gate",
                            "run_status": "completed",
                            "objective_status": "completed",
                            "support_gate_run_success_rate": 0.70,
                            "support_gate_run_available_ratio": 0.50,
                        }
                    )
                ],
            )

            result = _run_cli(
                [
                    "--input",
                    str(baseline_path),
                    "--compare-input",
                    str(candidate_path),
                    "--format",
                    "markdown",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("## Comparison", result.stdout)
            self.assertIn("- Confidence: low", result.stdout)
            self.assertIn("- Use more runs before trusting this comparison.", result.stdout)
            self.assertIn("- Recommendation: Candidate looks better for support_gate.", result.stdout)


if __name__ == "__main__":
    unittest.main()
