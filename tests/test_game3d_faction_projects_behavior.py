from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def _extract_projects(content: str) -> list[str]:
    match = re.search(r"ALLEGIANCE_PROJECT_TYPES:\s*Array\[String\]\s*=\s*\[([^\]]+)\]", content)
    if not match:
        raise AssertionError("ALLEGIANCE_PROJECT_TYPES list not found")
    raw = match.group(1)
    return [part.strip().strip('"') for part in raw.split(",") if part.strip()]


def pick_project_contract(
    *,
    world_event_id: str,
    doctrine: str,
    raid_role: str,
    faction: str,
    structure_state: str,
) -> str:
    if raid_role == "target":
        return "fortify"
    if raid_role == "source":
        return "warband_muster"
    if doctrine == "arcane" and world_event_id == "mana_surge":
        return "ritual_focus"
    if doctrine == "steadfast":
        return "fortify"
    if doctrine == "warlike":
        return "warband_muster"
    if doctrine == "arcane":
        return "ritual_focus"
    if structure_state == "monster_lair" or faction == "monster":
        return "warband_muster"
    return "fortify"


def project_modifier_contract(project_id: str) -> dict[str, float]:
    if project_id == "fortify":
        return {
            "raid_delta": -0.06,
            "defense_delta": 0.12,
            "rally_regroup_delta": 0.0,
            "magic_damage_mult": 1.00,
            "magic_cost_mult": 1.00,
        }
    if project_id == "warband_muster":
        return {
            "raid_delta": 0.09,
            "defense_delta": 0.0,
            "rally_regroup_delta": 0.07,
            "magic_damage_mult": 1.00,
            "magic_cost_mult": 1.00,
        }
    if project_id == "ritual_focus":
        return {
            "raid_delta": 0.0,
            "defense_delta": 0.0,
            "rally_regroup_delta": 0.0,
            "magic_damage_mult": 1.05,
            "magic_cost_mult": 0.95,
        }
    return {
        "raid_delta": 0.0,
        "defense_delta": 0.0,
        "rally_regroup_delta": 0.0,
        "magic_damage_mult": 1.00,
        "magic_cost_mult": 1.00,
    }


def can_start_project_contract(
    *,
    active_project: str,
    now: float,
    cooldown_until: float,
    chance_roll: float,
    start_chance: float,
) -> bool:
    if active_project != "":
        return False
    if now < cooldown_until:
        return False
    return chance_roll <= start_chance


def project_lifecycle_contract(
    *,
    active_project: str,
    now: float,
    end_at: float,
    allegiance_alive: bool,
) -> str:
    if active_project == "":
        return "none"
    if not allegiance_alive:
        return "interrupted"
    if now >= end_at:
        return "ended"
    return "active"


class TestGame3DFactionProjectsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.ai_content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.readme_content = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    def test_project_set_is_small_distinct_and_readable(self):
        projects = _extract_projects(self.world_content)
        self.assertGreaterEqual(len(projects), 2)
        self.assertLessEqual(len(projects), 3)
        self.assertEqual(len(set(projects)), len(projects))
        self.assertIn("fortify", projects)
        self.assertIn("warband_muster", projects)
        self.assertIn("ritual_focus", projects)

    def test_project_pick_contract_is_contextual_and_stable(self):
        self.assertEqual(
            pick_project_contract(
                world_event_id="",
                doctrine="steadfast",
                raid_role="target",
                faction="human",
                structure_state="human_outpost",
            ),
            "fortify",
        )
        self.assertEqual(
            pick_project_contract(
                world_event_id="monster_frenzy",
                doctrine="warlike",
                raid_role="source",
                faction="monster",
                structure_state="monster_lair",
            ),
            "warband_muster",
        )
        self.assertEqual(
            pick_project_contract(
                world_event_id="mana_surge",
                doctrine="arcane",
                raid_role="none",
                faction="human",
                structure_state="human_outpost",
            ),
            "ritual_focus",
        )

    def test_project_modifiers_are_lightweight(self):
        for project_id in ["fortify", "warband_muster", "ritual_focus"]:
            mod = project_modifier_contract(project_id)
            self.assertGreaterEqual(mod["raid_delta"], -0.15)
            self.assertLessEqual(mod["raid_delta"], 0.15)
            self.assertGreaterEqual(mod["defense_delta"], -0.15)
            self.assertLessEqual(mod["defense_delta"], 0.15)
            self.assertGreaterEqual(mod["rally_regroup_delta"], -0.15)
            self.assertLessEqual(mod["rally_regroup_delta"], 0.15)
            self.assertGreaterEqual(mod["magic_damage_mult"], 1.0)
            self.assertLessEqual(mod["magic_damage_mult"], 1.10)
            self.assertGreaterEqual(mod["magic_cost_mult"], 0.90)
            self.assertLessEqual(mod["magic_cost_mult"], 1.0)

    def test_runtime_contract_enforces_single_active_project_and_cooldown(self):
        self.assertFalse(
            can_start_project_contract(
                active_project="fortify",
                now=40.0,
                cooldown_until=0.0,
                chance_roll=0.01,
                start_chance=0.35,
            )
        )
        self.assertFalse(
            can_start_project_contract(
                active_project="",
                now=10.0,
                cooldown_until=15.0,
                chance_roll=0.01,
                start_chance=0.35,
            )
        )
        self.assertTrue(
            can_start_project_contract(
                active_project="",
                now=16.0,
                cooldown_until=15.0,
                chance_roll=0.20,
                start_chance=0.35,
            )
        )

    def test_runtime_contract_finishes_or_interrupts_cleanly(self):
        self.assertEqual(
            project_lifecycle_contract(
                active_project="warband_muster",
                now=25.0,
                end_at=24.0,
                allegiance_alive=True,
            ),
            "ended",
        )
        self.assertEqual(
            project_lifecycle_contract(
                active_project="ritual_focus",
                now=12.0,
                end_at=24.0,
                allegiance_alive=False,
            ),
            "interrupted",
        )

    def test_hooks_exist_in_runtime_ai_hud_and_docs(self):
        self.assertIn("ALLEGIANCE_PROJECT_TYPES", self.world_content)
        self.assertIn("get_allegiance_project", self.world_content)
        self.assertIn("get_allegiance_project_modifiers", self.world_content)
        self.assertIn("_update_allegiance_projects_runtime", self.world_content)
        self.assertIn("allegiance_project_started", self.world_content)
        self.assertIn("allegiance_project_ended", self.world_content)
        self.assertIn("allegiance_project_interrupted", self.world_content)
        self.assertIn("Project START", self.loop_content)
        self.assertIn("Project END", self.loop_content)
        self.assertIn("Project INTERRUPTED", self.loop_content)
        self.assertIn('"allegiance_project_counts"', self.loop_content)
        self.assertIn('"project_started_total"', self.loop_content)
        self.assertIn("get_allegiance_project_modifiers", self.ai_content)
        self.assertIn("Projects:", self.overlay_content)
        self.assertIn("Project map:", self.overlay_content)
        self.assertIn("project", self.readme_content)
        self.assertIn("fortify", self.readme_content)
        self.assertIn("warband_muster", self.readme_content)
        self.assertIn("ritual_focus", self.readme_content)


if __name__ == "__main__":
    unittest.main()
