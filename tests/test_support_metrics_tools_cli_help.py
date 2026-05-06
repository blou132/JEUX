from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "support_metrics_cli_help_expected.json"


class SupportMetricsToolsCliHelpTests(unittest.TestCase):
    def test_support_metrics_tools_expose_expected_help_options(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        tools = fixture.get("tools", [])
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

        for tool_entry in tools:
            self.assertIsInstance(tool_entry, dict)
            tool_path = ROOT / str(tool_entry.get("path", ""))
            expected_options = tool_entry.get("options", [])

            self.assertTrue(
                tool_path.exists(),
                msg=f"Tool path missing: {tool_path}",
            )
            self.assertIsInstance(expected_options, list)
            self.assertGreater(
                len(expected_options),
                0,
                msg=f"No expected options listed for {tool_path}",
            )

            result = subprocess.run(
                [sys.executable, str(tool_path), "--help"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
            combined_output_lower = combined_output.lower()

            self.assertEqual(
                result.returncode,
                0,
                msg=f"--help failed for {tool_path}\n{combined_output}",
            )
            self.assertNotEqual(
                combined_output.strip(),
                "",
                msg=f"--help output is empty for {tool_path}",
            )
            self.assertTrue(
                ("usage" in combined_output_lower) or ("options" in combined_output_lower),
                msg=f"--help output missing usage/options for {tool_path}\n{combined_output}",
            )
            self.assertNotIn(
                "traceback",
                combined_output_lower,
                msg=f"--help output contains traceback for {tool_path}\n{combined_output}",
            )

            for option in expected_options:
                self.assertIn(
                    option,
                    combined_output,
                    msg=f"Missing expected option {option!r} in --help for {tool_path}\n{combined_output}",
                )


if __name__ == "__main__":
    unittest.main()
