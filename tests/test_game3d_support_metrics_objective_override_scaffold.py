from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME_LOOP_PATH = ROOT / "game3d" / "scripts" / "core" / "GameLoop.gd"


class Game3DSupportMetricsObjectiveOverrideScaffoldTests(unittest.TestCase):
    def test_game_loop_contains_objective_override_cli_flag(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support-metrics-objective", content)

    def test_game_loop_contains_rally_champion_objective_for_runtime_override(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("rally_champion", content)

    def test_game_loop_contains_forced_objective_trace_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support_metrics_forced_objective", content)
        self.assertIn("support_metrics_forced_objective_enabled", content)
        self.assertIn("support_metrics_forced_objective_rejected", content)
        self.assertIn("support_metrics_forced_objective_reject_reason", content)

    def test_game_loop_keeps_debug_only_not_gameplay_metrics_note(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("debug only, not gameplay metrics", content)
        self.assertIn("probe only, not gameplay metrics", content)
        self.assertIn("forced objective rejected / unknown objective", content)


if __name__ == "__main__":
    unittest.main()

