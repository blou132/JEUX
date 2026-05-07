from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME_LOOP_PATH = ROOT / "game3d" / "scripts" / "core" / "GameLoop.gd"


class Game3DSupportMetricsProbeScaffoldTests(unittest.TestCase):
    def test_game_loop_contains_probe_cli_flag(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support-metrics-probe", content)

    def test_game_loop_contains_probe_output_file_name(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support_metrics_runtime_probe.json", content)

    def test_game_loop_probe_mentions_not_gameplay_metrics(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("not gameplay metrics", content)


if __name__ == "__main__":
    unittest.main()

