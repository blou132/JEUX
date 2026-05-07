from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME_LOOP_PATH = ROOT / "game3d" / "scripts" / "core" / "GameLoop.gd"


class Game3DSupportMetricsTraceScaffoldTests(unittest.TestCase):
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
        self.assertIn("export_function_reached", content)
        self.assertIn("history_append_attempted", content)
        self.assertIn("history_append_success", content)


if __name__ == "__main__":
    unittest.main()

