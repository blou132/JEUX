from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "inspect_support_metrics_runtime_entry.py"


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _run_tool(extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + extra_args,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class InspectSupportMetricsRuntimeEntryToolTests(unittest.TestCase):
    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--baseline", result.stdout)
        self.assertIn("--current", result.stdout)
        self.assertIn("--json", result.stdout)
        self.assertIn("--check", result.stdout)

    def test_inspects_top_level_runtime_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline.jsonl"
            current_path = Path(tmpdir) / "current.jsonl"
            row = {
                "export_trigger": "debug_export_on_quit",
                "debug_export_on_quit": True,
                "gameplay_change_allowed": False,
                "support_gate": {"run_attempts": 0},
                "champion_support": {"run_attempts": 0},
                "champion_resolution": {"resolved_state": "unresolved"},
                "missing_payload_fields": [],
                "payload_has_support_gate": "yes",
                "payload_has_champion_support": "yes",
                "payload_has_champion_resolution": "yes",
            }
            _write_jsonl(baseline_path, [row])
            _write_jsonl(current_path, [row])

            result = _run_tool(
                [
                    "--baseline",
                    str(baseline_path),
                    "--current",
                    str(current_path),
                    "--json",
                    "--check",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            baseline = payload["baseline"]
            self.assertIn("support_gate", baseline["top_level_keys"])
            self.assertIn("champion_support", baseline["top_level_keys"])
            self.assertIn("champion_resolution", baseline["top_level_keys"])
            self.assertTrue(baseline["has_support_gate"])
            self.assertTrue(baseline["has_champion_support"])
            self.assertTrue(baseline["has_champion_resolution"])
            self.assertEqual(baseline["paths"]["support_gate"], ["support_gate"])
            self.assertEqual(baseline["paths"]["champion_support"], ["champion_support"])
            self.assertEqual(baseline["paths"]["champion_resolution"], ["champion_resolution"])
            self.assertEqual(baseline["export_trigger"], "debug_export_on_quit")
            self.assertTrue(baseline["debug_export_on_quit"])
            self.assertFalse(baseline["gameplay_change_allowed"])
            self.assertEqual(baseline["missing_payload_fields"], [])
            self.assertEqual(baseline["payload_has_support_gate"], "yes")
            self.assertEqual(baseline["payload_has_champion_support"], "yes")
            self.assertEqual(baseline["payload_has_champion_resolution"], "yes")

    def test_inspects_nested_runtime_fields_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "baseline_nested.jsonl"
            current_path = Path(tmpdir) / "current_nested.jsonl"
            nested_row = {
                "export_trigger": "debug_export_on_quit",
                "debug_export_on_quit": True,
                "gameplay_change_allowed": False,
                "payload": {
                    "support_gate": {"run_attempts": 1},
                    "champion_resolution": {"run_resolved": 0},
                },
                "missing_payload_fields": ["champion_support"],
            }
            _write_jsonl(baseline_path, [nested_row])
            _write_jsonl(current_path, [nested_row])

            result = _run_tool(
                [
                    "--baseline",
                    str(baseline_path),
                    "--current",
                    str(current_path),
                    "--json",
                    "--check",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            baseline = payload["baseline"]
            self.assertTrue(baseline["has_support_gate"])
            self.assertFalse(baseline["has_champion_support"])
            self.assertTrue(baseline["has_champion_resolution"])
            self.assertIn("payload.support_gate", baseline["paths"]["support_gate"])
            self.assertIn("payload.champion_resolution", baseline["paths"]["champion_resolution"])
            self.assertEqual(baseline["missing_payload_fields"], ["champion_support"])

    def test_missing_file_with_check_returns_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = Path(tmpdir) / "missing_baseline.jsonl"
            current_path = Path(tmpdir) / "missing_current.jsonl"
            result = _run_tool(
                [
                    "--baseline",
                    str(baseline_path),
                    "--current",
                    str(current_path),
                    "--check",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("file not found", result.stdout)


if __name__ == "__main__":
    unittest.main()
