import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from debug_tools.batch_history import (
    append_batch_history,
    build_batch_history_entry,
    format_batch_history_summary,
    load_batch_history,
)


class BatchHistoryTests(unittest.TestCase):
    def test_append_and_load_history(self) -> None:
        batch_payload = {
            "mode": "batch",
            "batch_param": "energy_drain_rate",
            "batch_values": [1.0, 1.5],
            "runs_per_value": 2,
            "base_seed": 100,
            "seed_step": 3,
            "comparative_summary": {
                "most_stable": {"winners": [1.0]},
                "best_avg_max_generation": {"winners": [1.0]},
                "best_avg_final_population": {"winners": [1.0]},
                "lowest_extinction_rate": {"winners": [1.0, 1.5]},
            },
            "scenarios": [
                {
                    "parameter_value": 1.0,
                    "multi_run_summary": {
                        "runs": 2,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 2.5,
                        "avg_final_population": 42.5,
                    },
                },
                {
                    "parameter_value": 1.5,
                    "multi_run_summary": {
                        "runs": 2,
                        "extinction_rate": 0.0,
                        "avg_max_generation": 2.0,
                        "avg_final_population": 39.5,
                    },
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "batch_history.json"
            entry = build_batch_history_entry("exp_a", batch_payload)
            append_batch_history(str(history_path), entry)

            loaded = load_batch_history(str(history_path))
            self.assertEqual(int(loaded["schema_version"]), 1)
            self.assertEqual(len(loaded["experiments"]), 1)

            first = loaded["experiments"][0]
            self.assertEqual(first["id"], "exp_a")
            self.assertEqual(first["batch_param"], "energy_drain_rate")
            self.assertEqual(first["batch_values"], [1.0, 1.5])
            self.assertEqual(int(first["runs_per_value"]), 2)

            summary_text = format_batch_history_summary(loaded)
            self.assertIn("=== Batch History ===", summary_text)
            self.assertIn("id=exp_a", summary_text)
            self.assertIn("param=energy_drain_rate", summary_text)
            self.assertIn("comparatif:", summary_text)

    def test_duplicate_batch_id_raises(self) -> None:
        batch_payload = {
            "mode": "batch",
            "batch_param": "energy_drain_rate",
            "batch_values": [1.0],
            "runs_per_value": 1,
            "base_seed": 42,
            "seed_step": 1,
            "comparative_summary": {},
            "scenarios": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "batch_history.json"
            first = build_batch_history_entry("exp_dup", batch_payload)
            second = build_batch_history_entry("exp_dup", batch_payload)

            append_batch_history(str(history_path), first)
            with self.assertRaises(ValueError):
                append_batch_history(str(history_path), second)

    def test_cli_history_archive_and_reader(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "batch_history.json"

            base_cmd = [
                sys.executable,
                "main.py",
                "--batch-param",
                "energy_drain_rate",
                "--batch-runs",
                "1",
                "--seed",
                "100",
                "--seed-step",
                "3",
                "--steps",
                "20",
                "--log-interval",
                "10",
                "--batch-history-path",
                str(history_path),
            ]

            cmd_one = base_cmd + ["--batch-values", "1.0", "--batch-id", "exp_001"]
            cmd_two = base_cmd + ["--batch-values", "1.5", "--batch-id", "exp_002"]

            subprocess.run(
                cmd_one,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=180,
            )
            subprocess.run(
                cmd_two,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=180,
            )

            self.assertTrue(history_path.exists())

            analyze_cmd = [
                sys.executable,
                "analyze_batch_history.py",
                str(history_path),
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
            self.assertIn("=== Batch History ===", output)
            self.assertIn("experiences=2", output)
            self.assertIn("id=exp_001", output)
            self.assertIn("id=exp_002", output)


if __name__ == "__main__":
    unittest.main()
