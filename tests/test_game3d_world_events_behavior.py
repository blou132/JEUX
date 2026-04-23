from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


def _extract_float(content: str, pattern: str) -> float:
    match = re.search(pattern, content)
    if not match:
        raise AssertionError(f"Pattern not found: {pattern}")
    return float(match.group(1))


def _extract_event_types(content: str) -> list[str]:
    match = re.search(r"WORLD_EVENT_TYPES:\s*Array\[String\]\s*=\s*\[([^\]]+)\]", content)
    if not match:
        raise AssertionError("WORLD_EVENT_TYPES list not found")
    raw = match.group(1)
    return [part.strip().strip('"') for part in raw.split(",") if part.strip()]


def _extract_modifier_value(content: str, key: str) -> float:
    escaped = re.escape(f'modifiers["{key}"] = ')
    pattern = escaped + r"([0-9.]+)"
    return _extract_float(content, pattern)


def world_event_step_contract(state: dict, delta: float, next_event_id: str) -> dict:
    durations = {
        "mana_surge": 18.0,
        "monster_frenzy": 16.0,
        "sanctuary_calm": 20.0,
    }

    next_state = dict(state)
    if next_state["active_id"] == "":
        next_state["next_in"] = max(0.0, float(next_state["next_in"]) - delta)
        if next_state["next_in"] <= 0.0:
            next_state["active_id"] = next_event_id
            next_state["remaining"] = durations[next_event_id]
            next_state["started"] = int(next_state["started"]) + 1
            next_state["last_id"] = next_event_id
        return next_state

    next_state["remaining"] = max(0.0, float(next_state["remaining"]) - delta)
    if next_state["remaining"] <= 0.0:
        next_state["active_id"] = ""
        next_state["remaining"] = 0.0
        next_state["next_in"] = 32.0
        next_state["ended"] = int(next_state["ended"]) + 1
    return next_state


class TestGame3DWorldEventsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.magic_content = (GAME3D / "scripts" / "magic" / "MagicSystem.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.combat_content = (GAME3D / "scripts" / "combat" / "CombatSystem.gd").read_text(encoding="utf-8")
        self.world_content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")

    def test_world_event_types_are_exactly_three_and_distinct(self):
        event_types = _extract_event_types(self.loop_content)
        self.assertEqual(len(event_types), 3)
        self.assertEqual(len(set(event_types)), 3)
        self.assertIn("mana_surge", event_types)
        self.assertIn("monster_frenzy", event_types)
        self.assertIn("sanctuary_calm", event_types)

    def test_world_event_timing_is_bounded(self):
        start_delay = _extract_float(self.loop_content, r"WORLD_EVENT_START_DELAY:\s*float\s*=\s*([0-9.]+)")
        cooldown_min = _extract_float(self.loop_content, r"WORLD_EVENT_COOLDOWN_MIN:\s*float\s*=\s*([0-9.]+)")
        cooldown_max = _extract_float(self.loop_content, r"WORLD_EVENT_COOLDOWN_MAX:\s*float\s*=\s*([0-9.]+)")

        self.assertGreaterEqual(start_delay, 15.0)
        self.assertLessEqual(start_delay, 40.0)
        self.assertGreater(cooldown_max, cooldown_min)
        self.assertGreaterEqual(cooldown_min, 20.0)
        self.assertLessEqual(cooldown_max, 60.0)

    def test_world_event_modifier_values_are_lightweight(self):
        magic_damage_mult = _extract_modifier_value(self.loop_content, "magic_damage_mult")
        magic_cost_mult = _extract_modifier_value(self.loop_content, "magic_energy_cost_mult")
        monster_melee_mult = _extract_modifier_value(self.loop_content, "monster_melee_damage_mult")
        monster_speed_mult = _extract_modifier_value(self.loop_content, "monster_speed_mult")
        human_regen_bonus = _extract_modifier_value(self.loop_content, "human_energy_regen_per_sec")
        raid_global_mult = _extract_modifier_value(self.loop_content, "raid_pressure_global_mult")
        raid_monster_mult = _extract_modifier_value(self.loop_content, "raid_pressure_monster_mult")

        self.assertGreaterEqual(magic_damage_mult, 1.0)
        self.assertLessEqual(magic_damage_mult, 1.25)
        self.assertGreaterEqual(magic_cost_mult, 0.75)
        self.assertLessEqual(magic_cost_mult, 1.0)
        self.assertGreaterEqual(monster_melee_mult, 1.0)
        self.assertLessEqual(monster_melee_mult, 1.20)
        self.assertGreaterEqual(monster_speed_mult, 1.0)
        self.assertLessEqual(monster_speed_mult, 1.15)
        self.assertGreater(human_regen_bonus, 0.0)
        self.assertLessEqual(human_regen_bonus, 0.8)
        self.assertGreaterEqual(raid_global_mult, 0.85)
        self.assertLessEqual(raid_global_mult, 1.10)
        self.assertGreaterEqual(raid_monster_mult, 0.70)
        self.assertLessEqual(raid_monster_mult, 1.20)

    def test_scheduler_contract_starts_and_ends_without_overlap(self):
        state = {
            "active_id": "",
            "remaining": 0.0,
            "next_in": 2.0,
            "started": 0,
            "ended": 0,
            "last_id": "",
        }
        picks = ["mana_surge", "monster_frenzy", "sanctuary_calm", "mana_surge"]
        pick_index = 0

        for _ in range(80):
            next_event = picks[min(pick_index, len(picks) - 1)]
            previous_active = state["active_id"]
            state = world_event_step_contract(state, 1.0, next_event)
            if previous_active == "" and state["active_id"] != "":
                pick_index += 1

            active_count = 0 if state["active_id"] == "" else 1
            self.assertLessEqual(active_count, 1)
            self.assertGreaterEqual(state["remaining"], 0.0)
            self.assertGreaterEqual(state["next_in"], 0.0)

        self.assertGreaterEqual(int(state["started"]), 2)
        self.assertGreaterEqual(int(state["ended"]), 1)

    def test_world_event_effects_are_hooked_into_core_systems(self):
        self.assertIn("get_magic_modifiers", self.magic_content)
        self.assertIn("damage_mult", self.magic_content)
        self.assertIn("energy_cost_mult", self.magic_content)
        self.assertIn("get_melee_damage_multiplier", self.combat_content)
        self.assertIn("get_speed_multiplier", self.actor_content)
        self.assertIn("get_energy_regen_bonus_per_sec", self.actor_content)
        self.assertIn("set_raid_pressure_modifiers", self.world_content)
        self.assertIn("World Event START", self.loop_content)
        self.assertIn("World Event END", self.loop_content)


if __name__ == "__main__":
    unittest.main()
