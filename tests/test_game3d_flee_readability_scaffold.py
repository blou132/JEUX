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

    def test_actor_builds_in_world_flee_indicator(self) -> None:
        content = ACTOR_PATH.read_text(encoding="utf-8")
        self.assertIn("var flee_indicator_visible: bool = false", content)
        self.assertIn("var flee_indicator_pulse_visible: bool = false", content)
        self.assertIn("var _flee_indicator_root: Node3D = null", content)
        self.assertIn("var _flee_indicator_stem: MeshInstance3D = null", content)
        self.assertIn("var _flee_indicator_dot: MeshInstance3D = null", content)
        self.assertIn("var _flee_indicator_pulse: MeshInstance3D = null", content)
        self.assertIn("_build_flee_indicator_visual(body.position.y)", content)
        self.assertIn("func _build_flee_indicator_visual(body_height: float) -> void:", content)
        self.assertIn(
            "if _flee_indicator_root != null and is_instance_valid(_flee_indicator_root):",
            content,
        )
        self.assertIn("return", content)

    def test_flee_indicator_is_state_driven_and_urgency_aware(self) -> None:
        content = ACTOR_PATH.read_text(encoding="utf-8")
        self.assertIn("var is_fleeing: bool = state == \"flee\" and not is_dead", content)
        self.assertIn("_flee_indicator_root.visible = is_fleeing", content)
        self.assertIn("flee_indicator_visible = is_fleeing", content)
        self.assertIn("if not is_fleeing:", content)
        self.assertIn("flee_indicator_pulse_visible = false", content)
        self.assertIn("if flee_urgency >= 0.0:", content)
        self.assertIn("var high_urgency: bool = urgency >= 0.65", content)
        self.assertIn("_flee_indicator_pulse.visible = high_urgency", content)
        self.assertIn("flee_indicator_pulse_visible = high_urgency", content)
        self.assertIn("_flee_indicator_stem.scale = Vector3.ONE * (1.22 if high_urgency else 0.88)", content)
        self.assertIn("_flee_indicator_dot.scale = Vector3.ONE * (1.30 if high_urgency else 0.98)", content)

    def test_flee_indicator_debug_line_is_available_in_overlay(self) -> None:
        content = DEBUG_OVERLAY_PATH.read_text(encoding="utf-8")
        self.assertIn("func _build_flee_indicator_line(snapshot: Dictionary) -> String:", content)
        self.assertIn("Flee indicator: visible=%s urgency=%s pulse=%s", content)
        self.assertIn("var flee_indicator_line: String = _build_flee_indicator_line(snapshot)", content)
        self.assertIn("Active objective: %s status=%s target=%s", content)
        self.assertIn("lines.append(active_objective_summary)", content)

    def test_flee_indicator_reads_reason_and_threat_kind(self) -> None:
        content = ACTOR_PATH.read_text(encoding="utf-8")
        self.assertIn("match flee_threat_kind:", content)
        self.assertIn("if flee_reason == \"notoriety_avoid\":", content)
        self.assertIn("_apply_flee_indicator_material(_flee_indicator_stem, indicator_color", content)

    def test_snapshot_exposes_flee_debug_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn('"flee_feedback_label": flee_feedback_label', content)
        self.assertIn('"flee_reason": flee_reason', content)
        self.assertIn('"flee_threat_kind": flee_threat_kind', content)
        self.assertIn('"flee_threat_distance": flee_threat_distance', content)
        self.assertIn('"flee_urgency": flee_urgency', content)
        self.assertIn('"flee_indicator_visible": flee_indicator_visible', content)
        self.assertIn('"flee_indicator_pulse": flee_indicator_pulse', content)
        self.assertIn('"flee_indicator_summary": flee_indicator_summary', content)
        self.assertIn('"flee_readability": flee_readability', content)
        self.assertIn('"flee_readability_summary": flee_readability_summary', content)
        self.assertIn('"active": flee_feedback_actor != "none"', content)
        self.assertIn('"threat_distance": flee_threat_distance_value', content)
        self.assertIn('"active_objective_id": active_objective_id', content)
        self.assertIn('"active_objective_label": active_objective_label', content)
        self.assertIn('"active_objective_status": active_objective_status', content)
        self.assertIn('"active_objective_target": active_objective_target', content)
        self.assertIn('"active_objective_summary": active_objective_summary', content)

    def test_export_payload_exposes_flee_readability_fields(self) -> None:
        content = GAME_LOOP_PATH.read_text(encoding="utf-8")
        self.assertIn('"flee_feedback_label": str(snapshot.get("flee_feedback_label", ""))', content)
        self.assertIn('"flee_reason": str(snapshot.get("flee_reason", ""))', content)
        self.assertIn('"flee_threat_kind": str(snapshot.get("flee_threat_kind", ""))', content)
        self.assertIn('"flee_threat_distance": snapshot.get("flee_threat_distance", null)', content)
        self.assertIn('"flee_urgency": snapshot.get("flee_urgency", null)', content)
        self.assertIn('"flee_indicator_visible": bool(snapshot.get("flee_indicator_visible", false))', content)
        self.assertIn('"flee_indicator_pulse": bool(snapshot.get("flee_indicator_pulse", false))', content)
        self.assertIn('"flee_indicator_summary": str(snapshot.get("flee_indicator_summary", ""))', content)
        self.assertIn('"flee_readability": flee_readability_payload', content)
        self.assertIn('"active_objective_id": active_objective_id_value', content)
        self.assertIn('"active_objective_label": active_objective_label_value', content)
        self.assertIn('"active_objective_status": active_objective_status_value', content)
        self.assertIn('"active_objective_target": active_objective_target_value', content)
        self.assertIn('"active_objective_summary": active_objective_summary_value', content)

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
        self.assertIn(
            "v235 adds an in-world flee readability indicator. It does not change flee rules or balance.",
            content,
        )
        self.assertIn(
            "v236 validates the in-world flee indicator visibility. No flee logic or balance change.",
            content,
        )
        self.assertIn(
            "v237 improves active objective readability only; objective rules are unchanged.",
            content,
        )


if __name__ == "__main__":
    unittest.main()
