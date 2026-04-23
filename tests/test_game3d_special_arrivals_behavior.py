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


def _extract_int(content: str, pattern: str) -> int:
    match = re.search(pattern, content)
    if not match:
        raise AssertionError(f"Pattern not found: {pattern}")
    return int(match.group(1))


def collect_candidates_contract(
    *,
    world_event_id: str,
    outpost_dominance: float,
    lair_dominance: float,
    min_dominance: float,
    active_total: int,
    active_humans: int,
    active_monsters: int,
    max_active: int,
    max_active_per_faction: int,
) -> list[dict]:
    if active_total >= max_active:
        return []

    candidates: list[dict] = []
    if (
        world_event_id == "sanctuary_calm"
        and outpost_dominance >= min_dominance
        and active_humans < max_active_per_faction
    ):
        candidates.append({"variant_id": "summoned_hero", "faction": "human"})

    if (
        world_event_id == "monster_frenzy"
        and lair_dominance >= min_dominance
        and active_monsters < max_active_per_faction
    ):
        candidates.append({"variant_id": "calamity_invader", "faction": "monster"})

    return candidates


def attempt_spawn_contract(state: dict, candidates: list[dict], trigger_roll: float) -> tuple[dict, dict | None]:
    next_state = dict(state)
    next_state["cooldown_left"] = max(0.0, float(next_state["cooldown_left"]) - float(next_state["delta"]))

    if next_state["cooldown_left"] > 0.0:
        return next_state, None
    if int(next_state["active_total"]) >= int(next_state["max_active"]):
        return next_state, None
    if not candidates:
        return next_state, None
    if trigger_roll > float(next_state["trigger_chance"]):
        return next_state, None

    chosen = candidates[0]
    next_state["cooldown_left"] = float(next_state["cooldown_seconds"])
    next_state["active_total"] = int(next_state["active_total"]) + 1
    if chosen["faction"] == "human":
        next_state["active_humans"] = int(next_state["active_humans"]) + 1
    else:
        next_state["active_monsters"] = int(next_state["active_monsters"]) + 1
    next_state["started_total"] = int(next_state["started_total"]) + 1
    return next_state, chosen


class TestGame3DSpecialArrivalsBehavior(unittest.TestCase):
    def setUp(self) -> None:
        self.loop_content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.actor_content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.overlay_content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")

        self.cooldown = _extract_float(self.loop_content, r"SPECIAL_ARRIVAL_COOLDOWN:\s*float\s*=\s*([0-9.]+)")
        self.check_interval = _extract_float(self.loop_content, r"SPECIAL_ARRIVAL_CHECK_INTERVAL:\s*float\s*=\s*([0-9.]+)")
        self.trigger_chance = _extract_float(self.loop_content, r"SPECIAL_ARRIVAL_TRIGGER_CHANCE:\s*float\s*=\s*([0-9.]+)")
        self.min_dominance = _extract_float(self.loop_content, r"SPECIAL_ARRIVAL_MIN_DOMINANCE_SECONDS:\s*float\s*=\s*([0-9.]+)")
        self.max_active = _extract_int(self.loop_content, r"SPECIAL_ARRIVAL_MAX_ACTIVE:\s*int\s*=\s*([0-9]+)")
        self.max_active_per_faction = _extract_int(self.loop_content, r"SPECIAL_ARRIVAL_MAX_ACTIVE_PER_FACTION:\s*int\s*=\s*([0-9]+)")

    def test_special_arrival_constants_are_bounded_and_rare(self):
        self.assertGreaterEqual(self.cooldown, 50.0)
        self.assertLessEqual(self.cooldown, 140.0)
        self.assertGreaterEqual(self.check_interval, 2.0)
        self.assertLessEqual(self.check_interval, 6.0)
        self.assertGreaterEqual(self.trigger_chance, 0.20)
        self.assertLessEqual(self.trigger_chance, 0.50)
        self.assertGreaterEqual(self.min_dominance, 10.0)
        self.assertLessEqual(self.min_dominance, 30.0)
        self.assertLessEqual(self.max_active, 2)
        self.assertLessEqual(self.max_active_per_faction, 1)

    def test_candidate_selection_uses_world_event_and_structure_stability(self):
        human_candidates = collect_candidates_contract(
            world_event_id="sanctuary_calm",
            outpost_dominance=22.0,
            lair_dominance=0.0,
            min_dominance=self.min_dominance,
            active_total=0,
            active_humans=0,
            active_monsters=0,
            max_active=self.max_active,
            max_active_per_faction=self.max_active_per_faction,
        )
        self.assertEqual(human_candidates[0]["variant_id"], "summoned_hero")

        monster_candidates = collect_candidates_contract(
            world_event_id="monster_frenzy",
            outpost_dominance=0.0,
            lair_dominance=24.0,
            min_dominance=self.min_dominance,
            active_total=0,
            active_humans=0,
            active_monsters=0,
            max_active=self.max_active,
            max_active_per_faction=self.max_active_per_faction,
        )
        self.assertEqual(monster_candidates[0]["variant_id"], "calamity_invader")

        no_candidates = collect_candidates_contract(
            world_event_id="mana_surge",
            outpost_dominance=30.0,
            lair_dominance=30.0,
            min_dominance=self.min_dominance,
            active_total=0,
            active_humans=0,
            active_monsters=0,
            max_active=self.max_active,
            max_active_per_faction=self.max_active_per_faction,
        )
        self.assertEqual(no_candidates, [])

    def test_spawn_attempt_respects_cooldown_and_cap(self):
        state = {
            "cooldown_left": 0.0,
            "cooldown_seconds": self.cooldown,
            "delta": self.check_interval,
            "active_total": 0,
            "active_humans": 0,
            "active_monsters": 0,
            "max_active": self.max_active,
            "trigger_chance": self.trigger_chance,
            "started_total": 0,
        }
        candidates = [{"variant_id": "summoned_hero", "faction": "human"}]

        state, spawned = attempt_spawn_contract(state, candidates, trigger_roll=0.0)
        self.assertIsNotNone(spawned)
        self.assertEqual(state["started_total"], 1)
        self.assertGreater(state["cooldown_left"], 0.0)

        state, spawned = attempt_spawn_contract(state, candidates, trigger_roll=0.0)
        self.assertIsNone(spawned)
        self.assertEqual(state["started_total"], 1)

        state["cooldown_left"] = 0.0
        state["active_total"] = self.max_active
        state, spawned = attempt_spawn_contract(state, candidates, trigger_roll=0.0)
        self.assertIsNone(spawned)
        self.assertEqual(state["started_total"], 1)

    def test_special_arrival_integration_hooks_exist(self):
        self.assertIn('world_event_active_id == "sanctuary_calm"', self.loop_content)
        self.assertIn('world_event_active_id == "monster_frenzy"', self.loop_content)
        self.assertIn('_find_special_arrival_anchor("human_outpost")', self.loop_content)
        self.assertIn('_find_special_arrival_anchor("monster_lair")', self.loop_content)
        self.assertIn("Special Arrival START", self.loop_content)
        self.assertIn("Special Arrival FALLEN", self.loop_content)
        self.assertIn('"special_arrivals_active_total"', self.loop_content)
        self.assertIn("set_special_arrival", self.actor_content)
        self.assertIn("apply_special_arrival_bonus", self.actor_content)
        self.assertIn("special_tag", self.actor_content)
        self.assertIn("Special arrivals:", self.overlay_content)


if __name__ == "__main__":
    unittest.main()
