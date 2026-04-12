import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BatchExperimentModeTests(unittest.TestCase):
    def test_cli_batch_mode_outputs_summary_per_value(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cmd = [
            sys.executable,
            "main.py",
            "--batch-param",
            "energy_drain_rate",
            "--batch-values",
            "1.0,1.5",
            "--batch-runs",
            "2",
            "--seed",
            "100",
            "--seed-step",
            "3",
            "--steps",
            "30",
            "--log-interval",
            "15",
        ]

        completed = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
            timeout=180,
        )

        output = completed.stdout
        self.assertIn("=== Batch Experimental Mode ===", output)
        self.assertIn("param=energy_drain_rate", output)
        self.assertIn("--- Batch Value 1/2: energy_drain_rate=1.0 ---", output)
        self.assertIn("--- Batch Value 2/2: energy_drain_rate=1.5 ---", output)
        self.assertIn("--- Batch Summary ---", output)
        self.assertIn("energy_drain_rate=1.0 runs=2", output)
        self.assertIn("energy_drain_rate=1.5 runs=2", output)

    def test_batch_mode_json_export_created_and_coherent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "batch_experiment.json"
            cmd = [
                sys.executable,
                "main.py",
                "--batch-param",
                "energy_drain_rate",
                "--batch-values",
                "1.0,1.5",
                "--batch-runs",
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

            completed = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=180,
            )

            output = completed.stdout
            self.assertTrue(export_path.exists())
            self.assertIn("export:", output)

            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "batch")
            self.assertEqual(payload["batch_param"], "energy_drain_rate")
            self.assertEqual(payload["runs_per_value"], 2)
            self.assertEqual(payload["batch_values"], [1.0, 1.5])

            scenarios = payload["scenarios"]
            self.assertEqual(len(scenarios), 2)
            self.assertEqual(float(scenarios[0]["parameter_value"]), 1.0)
            self.assertEqual(float(scenarios[1]["parameter_value"]), 1.5)
            self.assertEqual(scenarios[0]["seeds"], [100, 103])
            self.assertEqual(int(scenarios[0]["multi_run_summary"]["runs"]), 2)
            self.assertEqual(int(scenarios[1]["multi_run_summary"]["runs"]), 2)


if __name__ == "__main__":
    unittest.main()
