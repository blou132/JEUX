from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "export_creature_profiles.py"


class CreatureProfilesExportToolTests(unittest.TestCase):
    def test_export_writes_expected_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "creatures.json"
            result = subprocess.run(
                ["py", str(SCRIPT), "--path", str(output_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            profiles = payload.get("profiles", [])
            self.assertEqual(len(profiles), 6)
            ids = {profile["id"] for profile in profiles}
            self.assertEqual(
                ids,
                {
                    "human_fighter",
                    "human_mage",
                    "human_scout",
                    "monster_standard",
                    "monster_brute",
                    "monster_ranged",
                },
            )

    def test_validate_only_reports_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "creatures.json"
            invalid_payload = {
                "version": 1,
                "schema": "creature_profiles_v1",
                "profiles": [{"id": "human_fighter"}],
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
