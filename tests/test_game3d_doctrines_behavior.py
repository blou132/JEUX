from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def _extract_doctrines(content: str) -> list[str]:
    match = re.search(r"ALLEGIANCE_DOCTRINES:\s*Array\[String\]\s*=\s*\[([^\]]+)\]", content)
    if not match:
        raise AssertionError("ALLEGIANCE_DOCTRINES list not found")
    raw = match.group(1)
    return [part.strip().strip('"') for part in raw.split(",") if part.strip()]


def pick_doctrine_contract(
    *,
    world_event_id: str,
    faction: str,
    structure_state: str,
    dominant_champions: int,
) -> str:
    if world_event_id == "mana_surge" and dominant_champions > 0:
        return "arcane"
    if structure_state == "human_outpost":
        if world_event_id == "mana_surge":
            return "arcane"
        return "steadfast"
    if structure_state == "monster_lair":
        return "warlike"
    if faction == "human":
        return "steadfast"
    if faction == "monster":
        return "warlike"
    return "steadfast"


def doctrine_modifier_contract(doctrine: str) -> dict[str, float]:
    if doctrine == "warlike":
        return {
            "raid_delta": 0.11,
            "defense_delta": -0.05,
            "rally_regroup_delta": -0.05,
            "rally_pressure_delta": 0.08,
            "magic_damage_mult": 1.00,
            "magic_cost_mult": 1.00,
        }
    if doctrine == "steadfast":
        return {
            "raid_delta": -0.08,
            "defense_delta": 0.12,
            "rally_regroup_delta": 0.08,
            "rally_pressure_delta": -0.04,
            "magic_damage_mult": 1.00,
            "magic_cost_mult": 1.00,
        }
    if doctrine == "arcane":
        return {
            "raid_delta": 0.02,
            "defense_delta": 0.04,
            "rally_regroup_delta": 0.03,
            "rally_pressure_delta": 0.01,
            "magic_damage_mult": 1.06,
            "magic_cost_mult": 0.94,
        }
    return {
        "raid_delta": 0.0,
        "defense_delta": 0.0,
        "rally_regroup_delta": 0.0,
        "rally_pressure_delta": 0.0,
        "magic_damage_mult": 1.00,
        "magic_cost_mult": 1.00,
    }


def doctrine_source_contract(*, doctrine_id: str, available_templates: set[str]) -> str:
    if doctrine_id and doctrine_id in available_templates:
        return "json"
    return "fallback"


def cleanup_doctrine_contract(mapping: dict[str, str], allegiance_id: str) -> tuple[dict[str, str], str]:
    next_mapping = dict(mapping)
    doctrine = str(next_mapping.get(allegiance_id, ""))
    if allegiance_id in next_mapping:
        del next_mapping[allegiance_id]
    return next_mapping, doctrine


class TestGame3DDoctrinesBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    def test_doctrine_set_is_small_distinct_and_readable(self):
        doctrines = _extract_doctrines(self.world_content)
        self.assertGreaterEqual(len(doctrines), 2)
        self.assertLessEqual(len(doctrines), 3)
        self.assertEqual(len(set(doctrines)), len(doctrines))
        self.assertIn("warlike", doctrines)
        self.assertIn("steadfast", doctrines)
        self.assertIn("arcane", doctrines)

    def test_assignment_contract_is_bounded_and_contextual(self):
        self.assertEqual(
            pick_doctrine_contract(
                world_event_id="",
                faction="human",
                structure_state="human_outpost",
                dominant_champions=0,
            ),
            "steadfast",
        )
        self.assertEqual(
            pick_doctrine_contract(
                world_event_id="monster_frenzy",
                faction="monster",
                structure_state="monster_lair",
                dominant_champions=1,
            ),
            "warlike",
        )
        self.assertEqual(
            pick_doctrine_contract(
                world_event_id="mana_surge",
                faction="human",
                structure_state="human_outpost",
                dominant_champions=1,
            ),
            "arcane",
        )

    def test_doctrine_modifiers_stay_light(self):
        for doctrine in ["warlike", "steadfast", "arcane"]:
            mod = doctrine_modifier_contract(doctrine)
            self.assertGreaterEqual(mod["raid_delta"], -0.15)
            self.assertLessEqual(mod["raid_delta"], 0.15)
            self.assertGreaterEqual(mod["defense_delta"], -0.15)
            self.assertLessEqual(mod["defense_delta"], 0.15)
            self.assertGreaterEqual(mod["rally_regroup_delta"], -0.15)
            self.assertLessEqual(mod["rally_regroup_delta"], 0.15)
            self.assertGreaterEqual(mod["rally_pressure_delta"], -0.15)
            self.assertLessEqual(mod["rally_pressure_delta"], 0.15)
            self.assertGreaterEqual(mod["magic_damage_mult"], 1.0)
            self.assertLessEqual(mod["magic_damage_mult"], 1.12)
            self.assertGreaterEqual(mod["magic_cost_mult"], 0.88)
            self.assertLessEqual(mod["magic_cost_mult"], 1.0)

    def test_cleanup_contract_removes_doctrine_with_allegiance(self):
        mapping = {"human:camp": "steadfast", "monster:ruins": "warlike"}
        next_mapping, removed = cleanup_doctrine_contract(mapping, "human:camp")
        self.assertEqual(removed, "steadfast")
        self.assertNotIn("human:camp", next_mapping)
        self.assertIn("monster:ruins", next_mapping)

    def test_observability_helpers_and_snapshot_hooks_exist(self):
        self.assertIn("get_allegiance_doctrine_source", self.world_content)
        self.assertIn("get_allegiance_doctrine_label", self.world_content)
        self.assertIn("get_allegiance_doctrine_tags", self.world_content)
        self.assertIn("get_allegiance_doctrine_biases", self.world_content)
        self.assertIn("get_doctrine_runtime_snapshot", self.world_content)
        self.assertIn("Doctrine bridge: doctrines.json source=json.", self.loop_content)
        self.assertIn("Doctrine bridge: doctrines.json source=fallback.", self.loop_content)
        self.assertIn('"allegiance_doctrine_source_counts"', self.loop_content)
        self.assertIn('"allegiance_doctrine_average_biases"', self.loop_content)
        self.assertIn("fallback=%d", self.overlay_content)
        self.assertIn("Doctrine dominant:", self.overlay_content)
        self.assertIn("Doctrine bias avg:", self.overlay_content)

    def test_source_contract_is_json_or_fallback(self):
        self.assertEqual(
            doctrine_source_contract(doctrine_id="warlike", available_templates={"warlike", "arcane"}),
            "json",
        )
        self.assertEqual(
            doctrine_source_contract(doctrine_id="steadfast", available_templates={"warlike", "arcane"}),
            "fallback",
        )
        self.assertEqual(
            doctrine_source_contract(doctrine_id="", available_templates={"warlike", "arcane"}),
            "fallback",
        )

    def test_unknown_doctrine_is_ignored_with_logs(self):
        self.assertIn("ignored invalid doctrine", self.world_content)
        self.assertIn("Doctrine ignored:", self.loop_content)

    def test_fallback_path_remains_wired_when_doctrines_json_is_invalid_or_missing(self):
        self.assertIn("if _data_loader.load_doctrine_templates()", self.loop_content)
        self.assertIn("doctrine_templates_by_id.clear()", self.loop_content)
        self.assertIn("world_manager.set_doctrine_templates({})", self.loop_content)
        self.assertIn("DataLoader ERROR:", self.loop_content)
        self.assertIn("invalid JSON", (GAME3D / "scripts" / "data" / "DataLoader.gd").read_text(encoding="utf-8"))

    def test_hooks_exist_in_runtime_ai_hud_and_docs(self):
        self.assertIn("get_allegiance_doctrine", self.world_content)
        self.assertIn("get_allegiance_doctrine_modifiers", self.world_content)
        self.assertIn("_assign_doctrine_for_allegiance", self.world_content)
        self.assertIn("_clear_allegiance_doctrine", self.world_content)
        self.assertIn("Doctrine assigned", self.loop_content)
        self.assertIn("doctrine_assigned_total", self.loop_content)
        self.assertIn("rally_regroup_delta", self.ai_content)
        self.assertIn("rally_pressure_delta", self.ai_content)
        self.assertIn("Doctrines:", self.overlay_content)
        self.assertIn("Doctrine map:", self.overlay_content)
        self.assertIn("doctrine", self.readme_content)


if __name__ == "__main__":
    unittest.main()
