import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ExportResultsTests(unittest.TestCase):
    def test_single_run_json_export_created_and_coherent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "single_run_summary.json"
            cmd = [
                sys.executable,
                "main.py",
                "--runs",
                "1",
                "--seed",
                "42",
                "--steps",
                "20",
                "--log-interval",
                "10",
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
                timeout=120,
            )

            output = completed.stdout
            self.assertTrue(export_path.exists())
            self.assertIn("--- Run Summary ---", output)
            self.assertIn("export:", output)

            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "single")
            self.assertEqual(int(payload["seed"]), 42)
            self.assertIn("run_summary", payload)

            dominant_signature = str(payload["run_summary"].get("final_dominant_group_signature", "-"))
            self.assertIn(f"dominant_final={dominant_signature}", output)

    def test_multi_run_json_export_created_and_coherent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "multi_run_summary.json"
            cmd = [
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

            completed = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

            output = completed.stdout
            self.assertTrue(export_path.exists())
            self.assertIn("=== Multi-Run Mode ===", output)
            self.assertIn("--- Multi-Run Summary ---", output)
            self.assertIn("seeds: 100,103", output)
            self.assertIn("export:", output)

            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "multi")
            self.assertEqual(payload["seeds"], [100, 103])
            self.assertEqual(int(payload["run_count"]), 2)
            self.assertEqual(len(payload["per_run"]), 2)

            multi_summary = payload["multi_run_summary"]
            self.assertEqual(int(multi_summary["runs"]), 2)
            extinctions = int(multi_summary["extinction_count"])
            self.assertIn(f"extinctions={extinctions}/2", output)

    def test_single_run_csv_export_created(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "single_run_summary.csv"
            cmd = [
                sys.executable,
                "main.py",
                "--runs",
                "1",
                "--seed",
                "42",
                "--steps",
                "20",
                "--log-interval",
                "10",
                "--export-path",
                str(export_path),
                "--export-format",
                "csv",
            ]

            subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

            self.assertTrue(export_path.exists())
            with export_path.open("r", encoding="utf-8", newline="") as file_obj:
                reader = csv.DictReader(file_obj)
                rows = list(reader)
                self.assertTrue(reader.fieldnames is not None)
                self.assertIn("mode", reader.fieldnames)
                self.assertIn("run_summary.final_dominant_group_signature", reader.fieldnames)
                self.assertGreaterEqual(len(rows), 1)
                self.assertEqual(rows[0].get("mode"), "single")


if __name__ == "__main__":
    unittest.main()
