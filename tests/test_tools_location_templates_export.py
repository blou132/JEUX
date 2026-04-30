from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "export_location_templates.py"


class LocationTemplatesExportToolTests(unittest.TestCase):
    def test_export_writes_expected_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "locations.json"
            result = subprocess.run(
                ["py", str(SCRIPT), "--path", str(output_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            locations = payload.get("locations", [])
            self.assertEqual(len(locations), 3)
            ids = {template["id"] for template in locations}
            self.assertEqual(ids, {"camp", "ruins", "rift_gate"})

    def test_validate_only_reports_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "locations.json"
            invalid_payload = {
                "version": 1,
                "schema": "location_templates_v1",
                "locations": [{"id": "camp"}],
            }
            output_path.write_text(json.dumps(invalid_payload, indent=2), encoding="utf-8")

            result = subprocess.run(
                ["py", str(SCRIPT), "--path", str(output_path), "--validate-only"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            combined = (result.stdout + result.stderr).lower()
            self.assertIn("validation failed", combined)


if __name__ == "__main__":
    unittest.main()
