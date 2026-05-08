from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME_LOOP_PATH = ROOT / "game3d" / "scripts" / "core" / "GameLoop.gd"


class Game3DSupportMetricsTraceScaffoldTests(unittest.TestCase):
    def test_game_loop_contains_export_on_quit_cli_flag(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support-metrics-export-on-quit", content)

    def test_game_loop_contains_trace_export_cli_flag(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support-metrics-trace-export", content)

    def test_game_loop_contains_trace_output_file_name(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("support_metrics_runtime_export_trace.json", content)

    def test_game_loop_trace_mentions_debug_only_not_gameplay_metrics(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("debug only, not gameplay metrics", content)

    def test_game_loop_trace_contains_export_path_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("export_trigger", content)
        self.assertIn("export_function_reached", content)
        self.assertIn("export_payload_built", content)
        self.assertIn("history_append_attempted", content)
        self.assertIn("history_append_success", content)

    def test_game_loop_trace_contains_debug_export_payload_markers(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("debug_export_on_quit", content)
        self.assertIn('"gameplay_change_allowed": false', content)
        self.assertIn('"champion_support_cooldown": champion_support_run_cooldown', content)
        self.assertIn('"champion_support_unavailable": champion_support_run_unavailable', content)
        self.assertIn('"champion_resolution": champion_resolution_payload', content)
        self.assertIn('"support_gate": support_gate_payload', content)

    def test_game_loop_trace_contains_payload_completeness_markers(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("payload_has_support_gate", content)
        self.assertIn("payload_has_champion_support", content)
        self.assertIn("payload_has_champion_resolution", content)
        self.assertIn("missing_payload_fields", content)

    def test_game_loop_keeps_champion_support_cooldown_constant(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "const OBJECTIVE_CHAMPION_SUPPORT_INTERACTION_COOLDOWN: float = 1.08",
            content,
        )


if __name__ == "__main__":
    unittest.main()
