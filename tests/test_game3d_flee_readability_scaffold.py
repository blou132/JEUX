from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"
AGENT_AI_PATH = GAME3D / "scripts" / "ai" / "AgentAI.gd"
ACTOR_PATH = GAME3D / "scripts" / "entities" / "Actor.gd"
GAME_LOOP_PATH = GAME3D / "scripts" / "core" / "GameLoop.gd"
DEBUG_OVERLAY_PATH = GAME3D / "scripts" / "ui" / "DebugOverlay.gd"
README_PATH = ROOT / "README.md"


class Game3DFleeReadabilityScaffoldTests(unittest.TestCase):
    def test_flee_priority_remains_ahead_of_offensive_branches(self) -> None:
        content = AGENT_AI_PATH.read_text(encoding="utf-8")
        under_pressure_idx = content.find("if under_pressure and distance <= actor.vision_range * 0.9:")
        cast_control_idx = content.find("if actor.can_cast_control()")
        self.assertNotEqual(under_pressure_idx, -1)
        self.assertNotEqual(cast_control_idx, -1)
        self.assertLess(under_pressure_idx, cast_control_idx)
        self.assertNotIn('"state": "hunger"', content)
        self.assertNotIn('"state": "reproduction"', content)

    def test_actor_exposes_flee_debug_fields(self) -> None:
        content = ACTOR_PATH.read_text(encoding="utf-8")
        self.assertIn("var flee_reason: String = \"\"", content)
        self.assertIn("var flee_threat_kind: String = \"\"", content)
        self.assertIn("var flee_threat_distance: float = -1.0", content)
        self.assertIn("var flee_urgency: float = -1.0", content)
        self.assertIn("_update_flee_debug_context(decision)", content)

    def test_snapshot_exposes_flee_debug_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn('"flee_feedback_label": flee_feedback_label', content)
        self.assertIn('"flee_reason": flee_reason', content)
        self.assertIn('"flee_threat_kind": flee_threat_kind', content)
        self.assertIn('"flee_threat_distance": flee_threat_distance', content)
        self.assertIn('"flee_urgency": flee_urgency', content)
        self.assertIn('"flee_readability": flee_readability', content)
        self.assertIn('"flee_readability_summary": flee_readability_summary', content)
        self.assertIn('"active": flee_feedback_actor != "none"', content)
        self.assertIn('"threat_distance": flee_threat_distance_value', content)

    def test_export_payload_exposes_flee_readability_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn('"flee_feedback_label": str(snapshot.get("flee_feedback_label", ""))', content)
        self.assertIn('"flee_reason": str(snapshot.get("flee_reason", ""))', content)
        self.assertIn('"flee_threat_kind": str(snapshot.get("flee_threat_kind", ""))', content)
        self.assertIn('"flee_threat_distance": snapshot.get("flee_threat_distance", null)', content)
        self.assertIn('"flee_urgency": snapshot.get("flee_urgency", null)', content)
        self.assertIn('"flee_readability": flee_readability_payload', content)

    def test_debug_overlay_renders_flee_feedback(self) -> None:
        content = DEBUG_OVERLAY_PATH.read_text(encoding="utf-8")
        self.assertIn("func _build_flee_feedback_line(snapshot: Dictionary) -> String:", content)
        self.assertIn("Flee readability: reason=%s threat=%s distance=%s urgency=%s", content)

    def test_transition_log_contains_flee_readability_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("threat_distance_label", content)
        self.assertIn("urgency_label", content)
        self.assertIn("dist=%s, urgency=%s", content)
        self.assertIn("threat=%s", content)

    def test_run_summary_can_include_flee_readability_line(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn("func _build_flee_readability_summary_line() -> String:", content)
        self.assertIn("Flee readability: reason=%s threat=%s distance=%s urgency=%s.", content)
        self.assertIn("run_summary_lines.append(flee_readability_line)", content)

    def test_sensitive_gameplay_constants_unchanged(self) -> None:
        game_loop = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "const OBJECTIVE_CHAMPION_SUPPORT_INTERACTION_COOLDOWN: float = 1.08",
            game_loop,
        )

    def test_support_gate_contract_fragments_still_present(self) -> None:
        game_loop = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn('"support_gate": support_gate_payload', game_loop)
        self.assertIn('"support_gate_run_success_rate": float(snapshot.get("support_gate_run_success_rate", 0.0))', game_loop)

    def test_readme_mentions_v232_readability_only(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        self.assertIn("v232 improves threat/flee readability only", content)
        self.assertIn("flee rules unchanged", content)
        self.assertIn("v233 validates flee/threat readability in runtime/debug outputs", content)
        self.assertIn("runtime readability only, no flee logic change", content)


if __name__ == "__main__":
    unittest.main()
