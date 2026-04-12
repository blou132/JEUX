import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from debug_tools import export_results
from debug_tools.export_analysis import load_export_payload, summarize_export_payload


class ExportAnalysisTests(unittest.TestCase):
    def test_load_single_json_and_build_summary(self) -> None:
        payload = {
            "mode": "single",
            "seed": 77,
            "extinct": False,
            "max_generation": 5,
            "final_alive": 31,
            "run_summary": {
                "final_dominant_group_signature": "gA",
                "final_dominant_group_share": 0.42,
                "most_stable_group_signature": "gA",
                "most_stable_group_count": 3,
                "most_rising_group_signature": "gC",
                "most_rising_group_count": 2,
                "final_zone_distribution": {"rich": 10, "neutral": 7, "poor": 4},
                "avg_traits": {
                    "speed": 1.01,
                    "metabolism": 0.98,
                    "prudence": 1.02,
                    "dominance": 1.03,
                    "repro_drive": 0.99,
                },
                "observed_logs": 6,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "single.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "single")
        self.assertEqual(int(loaded["seed"]), 77)
        self.assertIn("=== Export Analysis (single) ===", summary)
        self.assertIn("seed=77", summary)
        self.assertIn("synthese_run:", summary)
        self.assertIn("dominant_final=gA", summary)

    def test_load_multi_json_and_build_summary(self) -> None:
        payload = {
            "mode": "multi",
            "seeds": [10, 11, 12],
            "run_count": 3,
            "multi_run_summary": {
                "runs": 3,
                "seeds": [10, 11, 12],
                "extinction_count": 1,
                "extinction_rate": 1.0 / 3.0,
                "avg_max_generation": 6.0,
                "avg_final_population": 24.0,
                "avg_final_traits": {
                    "speed": 1.0,
                    "metabolism": 1.0,
                    "prudence": 1.0,
                    "dominance": 1.0,
                    "repro_drive": 1.0,
                },
                "most_frequent_final_dominant_group": "gA",
                "most_frequent_final_dominant_group_count": 2,
                "most_frequent_final_dominant_group_share": 2.0 / 3.0,
            },
            "per_run": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "multi.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "multi")
        self.assertEqual(loaded["seeds"], [10, 11, 12])
        self.assertIn("=== Export Analysis (multi) ===", summary)
        self.assertIn("runs=3 seeds=10,11,12", summary)
        self.assertIn("multi_runs:", summary)
        self.assertIn("extinctions=1/3", summary)

    def test_load_batch_json_and_build_summary(self) -> None:
        payload = {
            "mode": "batch",
            "batch_param": "energy_drain_rate",
            "batch_values": [1.0, 1.5],
            "runs_per_value": 2,
            "comparative_summary": {
                "batch_param": "energy_drain_rate",
                "evaluated_values_count": 2,
                "most_stable": {
                    "winners": [1.0],
                    "extinction_rate": 0.0,
                    "avg_final_population": 44.5,
                    "avg_max_generation": 3.0,
                },
                "best_avg_max_generation": {
                    "winners": [1.0],
                    "avg_max_generation": 3.0,
                },
                "best_avg_final_population": {
                    "winners": [1.0],
                    "avg_final_population": 44.5,
                },
                "lowest_extinction_rate": {
                    "winners": [1.0, 1.5],
                    "extinction_rate": 0.0,
                },
            },
            "scenarios": [
                {
                    "parameter_value": 1.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 0,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 3.0,
                        "avg_final_population": 44.5,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "most_frequent_final_dominant_group": "gA",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
                {
                    "parameter_value": 1.5,
                    "multi_run_summary": {
                        "runs": 2,
                        "seeds": [100, 103],
                        "extinction_count": 1,
                        "extinction_rate": 0.5,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 20.0,
                        "avg_final_traits": {
                            "speed": 1.0,
                            "metabolism": 1.0,
                            "prudence": 1.0,
                            "dominance": 1.0,
                            "repro_drive": 1.0,
                        },
                        "most_frequent_final_dominant_group": "gB",
                        "most_frequent_final_dominant_group_count": 1,
                        "most_frequent_final_dominant_group_share": 0.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export_payload(str(path))
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "batch")
        self.assertIn("=== Export Analysis (batch) ===", summary)
        self.assertIn("param=energy_drain_rate values=1.0,1.5 runs_per_value=2", summary)
        self.assertIn("energy_drain_rate=1.0", summary)
        self.assertIn("energy_drain_rate=1.5", summary)
        self.assertIn("--- Batch Comparative Summary ---", summary)
        self.assertIn("batch_comparatif:", summary)
        self.assertIn("plus_stable:", summary)

    def test_load_multi_csv_preserves_memory_impact(self) -> None:
        payload = {
            "mode": "multi",
            "seeds": [10, 11],
            "run_count": 2,
            "multi_run_summary": {
                "runs": 2,
                "seeds": [10, 11],
                "extinction_count": 0,
                "extinction_rate": 0.0,
                "avg_max_generation": 5.0,
                "avg_final_population": 20.0,
                "avg_final_traits": {
                    "speed": 1.0,
                    "metabolism": 1.0,
                    "prudence": 1.0,
                    "dominance": 1.0,
                    "repro_drive": 1.0,
                },
                "avg_memory_impact": {
                    "food_usage_total": 8.0,
                    "danger_usage_total": 3.0,
                    "food_active_share": 0.25,
                    "danger_active_share": 0.15,
                    "food_effect_avg_distance": 1.2,
                    "danger_effect_avg_distance": 0.6,
                    "food_usage_per_tick": 0.4,
                    "danger_usage_per_tick": 0.2,
                },
                "most_frequent_final_dominant_group": "gA",
                "most_frequent_final_dominant_group_count": 2,
                "most_frequent_final_dominant_group_share": 1.0,
            },
            "per_run": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "multi.csv"
            export_results(payload, str(path), "csv")

            loaded = load_export_payload(str(path), input_format="csv")
            summary = summarize_export_payload(loaded)

        self.assertEqual(loaded["mode"], "multi")
        avg_memory = loaded["multi_run_summary"]["avg_memory_impact"]
        self.assertAlmostEqual(float(avg_memory["food_usage_total"]), 8.0)
        self.assertAlmostEqual(float(avg_memory["danger_usage_total"]), 3.0)
        self.assertIn("memoire_moy:", summary)

    def test_cli_analysis_on_real_export_json(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "run_export.json"

            run_cmd = [
                sys.executable,
                "main.py",
                "--runs",
                "2",
                "--seed",
                "100",
                "--seed-step",
                "3",
                "--steps",
                "30",
                "--log-interval",
                "15",
                "--export-path",
                str(export_path),
                "--export-format",
                "json",
            ]
            subprocess.run(
                run_cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

            analyze_cmd = [
                sys.executable,
                "analyze_export.py",
                str(export_path),
            ]
            completed = subprocess.run(
                analyze_cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

            output = completed.stdout
            self.assertIn("=== Export Analysis (multi) ===", output)
            self.assertIn("runs=2 seeds=100,103", output)
            self.assertIn("multi_runs:", output)


if __name__ == "__main__":
    unittest.main()
