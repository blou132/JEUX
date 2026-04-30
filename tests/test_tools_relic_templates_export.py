from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "export_relic_templates.py"


class RelicTemplatesExportToolTests(unittest.TestCase):
    def test_export_writes_expected_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "relics.json"
            result = subprocess.run(
                ["py", str(SCRIPT), "--path", str(output_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            relics = payload.get("relics", [])
            self.assertEqual(len(relics), 2)
            ids = {template["id"] for template in relics}
            self.assertEqual(ids, {"arcane_sigil", "oath_standard"})

    def test_validate_only_reports_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "relics.json"
            invalid_payload = {
                "version": 1,
                "schema": "relic_templates_v1",
                "relics": [{"id": "arcane_sigil"}],
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
